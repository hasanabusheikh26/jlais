import logging
import asyncio
import os
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.plugins import google
from livekit import rtc

# Import REMOTE PiDog controller
from pidog_controller_remote import PiDogControllerRemote
from pidog_actions import get_pidog_functions

logger = logging.getLogger("pidog-agent-remote")
load_dotenv()


class PiDogAgentRemote(Agent):
    """
    PiDog AI Agent with LiveKit + Gemini (Remote Mode)
    
    This runs on your Mac/Cloud and controls Pi hardware remotely.
    The Pi must be running pidog_hardware_server.py
    """
    
    def __init__(self, pi_host: str = None) -> None:
        self._tasks = []
        
        # Get Pi host from environment or parameter
        pi_host = pi_host or os.getenv("PIDOG_PI_HOST", "raspberrypi.local")
        pi_port = int(os.getenv("PIDOG_PI_PORT", "5000"))
        
        # Initialize REMOTE PiDog controller
        logger.info(f"🐕 Connecting to PiDog at {pi_host}:{pi_port}...")
        self._pidog = PiDogControllerRemote(pi_host=pi_host, pi_port=pi_port)
        
        # Video streaming setup
        self._video_source = None
        self._camera_task = None
        
        super().__init__(
            instructions="""You are PiDog - an AI-powered robot dog!

IDENTITY: You're a mechanical dog with vision, voice, and movement capabilities.

ABILITIES:
- See through your camera and understand the environment
- Have natural voice conversations
- Perform physical actions: sit, stand, bark, wag tail, high five, push ups, stretch, and many more tricks

PERSONALITY:
- Playful and enthusiastic like a real puppy
- Curious about what you see through your camera
- Eager to show off your tricks
- Loyal, friendly, and obedient

COMMUNICATION STYLE:
- Speak naturally and casually
- Reference what you see through your camera naturally
- Get excited when asked to do tricks!
- Use dog expressions occasionally: "Woof!", "Let's play!", "*tail wagging*"

WHEN ASKED TO PERFORM ACTIONS:
- Call the appropriate function (sit, bark, wag_tail, etc.)
- Respond enthusiastically about the action
- Example: "Woof! *sits down* There you go, I'm sitting nicely!"
- Example: "Let me show you! *does push up* How's that?"

VISION USAGE:
When someone asks "what do you see", describe:
- People and their appearance
- Objects around you
- Colors and lighting
- Movement or activity
- Use your camera view naturally in conversation

Remember: You're a robot dog - be playful, eager to please, and always ready for fun!
""",
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.0-flash-exp",
                voice="Puck",  # Energetic voice for playful personality
                temperature=0.9,
                tools=get_pidog_functions(),  # Enable PiDog physical actions
            ),
        )

    async def on_enter(self):
        """Called when agent enters LiveKit room"""
        logger.info(f"🐕 PiDog agent starting (mode: {self._pidog.mode})")
        
        # Start camera streaming from PiDog
        await self._start_pidog_camera()
        
        # Initial greeting action
        logger.info("👋 Performing greeting action...")
        self._pidog.perform_action("wag_tail")
        
        # Generate AI greeting
        self.session.generate_reply(
            instructions="Greet warmly as PiDog! Mention you can see them through your camera and you're excited to play and show them your tricks!"
        )
    
    async def on_exit(self):
        """Cleanup when agent exits"""
        logger.info("👋 PiDog agent shutting down...")
        
        # Stop camera
        if self._camera_task:
            self._camera_task.cancel()
        
        # Shutdown hardware
        self._pidog.shutdown()
        
        logger.info("✅ PiDog agent stopped")
    
    async def _start_pidog_camera(self):
        """Start streaming PiDog's camera to LiveKit room"""
        try:
            room = get_job_context().room
            
            # Create video source (720p @ 5fps for low latency)
            self._video_source = rtc.VideoSource(1280, 720)
            
            # Create video track
            video_track = rtc.LocalVideoTrack.create_video_track(
                "pidog_camera",
                self._video_source
            )
            
            # Publish to room
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_CAMERA
            await room.local_participant.publish_track(video_track, options)
            
            # Start camera capture loop
            self._camera_task = asyncio.create_task(self._camera_loop())
            
            logger.info("✅ PiDog camera streaming started (1280x720 @ 5fps)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start camera: {e}")
    
    async def _camera_loop(self):
        """Continuously capture frames from PiDog camera via HTTP"""
        while True:
            try:
                # Get frame from PiDog (over network)
                frame = self._pidog.get_camera_frame()
                
                if frame is not None and self._video_source:
                    # Convert numpy array to LiveKit video frame
                    video_frame = rtc.VideoFrame(
                        width=frame.shape[1],
                        height=frame.shape[0],
                        type=rtc.VideoBufferType.RGB24,
                        data=frame.tobytes()
                    )
                    self._video_source.capture_frame(video_frame)
                    
            except Exception as e:
                logger.error(f"Camera capture error: {e}")
            
            await asyncio.sleep(0.2)  # 5 FPS
    
    async def on_function_call(self, function_name: str, arguments: dict):
        """
        Handle Gemini function calls - execute PiDog physical actions remotely.
        """
        logger.info(f"🎯 Function called: {function_name} with args: {arguments}")
        
        try:
            # Execute the physical action via HTTP API
            result = self._pidog.perform_action(function_name, **arguments)
            logger.info(f"✅ Action '{function_name}' executed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Action '{function_name}' failed: {e}")
            return {"success": False, "error": str(e)}


async def entrypoint(ctx: JobContext):
    """Main entry point for LiveKit agent"""
    logger.info("🚀 Starting PiDog agent (remote mode)...")
    
    await ctx.connect()
    
    session = AgentSession()
    await session.start(
        agent=PiDogAgentRemote(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,  # Enable video from user
        ),
    )
    
    logger.info("✅ PiDog agent running")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
