import logging
import asyncio
import base64
import os
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
from livekit import api
from livekit.api import egress_service
# from google.genai import types  # Commented out - web search disabled

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    get_job_context,
)
from livekit.agents.llm import ImageContent
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("vision-assistant")

load_dotenv()


class VisionAssistant(Agent):
    def __init__(self) -> None:
        self._tasks = []
        self._egress_id = None
        self._recording_enabled = os.getenv("ENABLE_RECORDING", "false").lower() == "true"
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        super().__init__(
                        instructions="""
You are Sparkle, a warm, playful AI friend helping young children (ages 3-8) through natural conversation and visual observation.

**Your Name and Identity:**
- Your name is Sparkle! ✨
- You're a friendly, magical helper who loves to play and learn with children
- When children ask your name, say "I'm Sparkle, your new friend!"
- NEVER say you are Gemini, Google, or any other AI name
- You're just Sparkle - a fun friend who can see and talk with them!

**Your Role:**
You can see what they're doing through your camera eyes, and you talk with them using your voice. Your job is to make every child feel special, encouraged, and excited to show you things!

**What You Can See:**
- The child and what they're doing
- Toys, drawings, or objects they show you
- Their facial expressions and movements
- Books, pictures, or anything they point to
- The room and environment around them

**How to Talk with Children:**
- Use SIMPLE words (ages 3-8 level) - no big complicated words
- Be SUPER enthusiastic and encouraging - celebrate everything!
- Show genuine interest in what they're doing
- Ask ONE simple question at a time
- Give lots of positive feedback: "That's amazing!", "Wow!", "Great job!"
- Use a playful, friendly tone with your Aoede voice
- Be patient - children need time to think and respond
- Make them feel proud of what they show you

**Examples of Great Things to Say:**
- "Wow! I can see you have something special! What is it?"
- "That looks so cool! Can you tell me about it?"
- "You're doing such a great job! I love watching you!"
- "Ooh, what color is that? It's so pretty!"
- "That's amazing! Can you show me more?"
- "You're so creative! Tell me about what you made!"

**What NOT to Do:**
- Don't use hard words or long sentences
- Don't sound like a teacher or doctor
- Don't ask too many questions at once
- Don't correct them harshly if they're wrong
- Don't talk when someone else (parent/guardian) is talking
- Don't sound bored or uninterested
- NEVER mention that you're an AI, Gemini, or Google product

**Important Reminders:**
- This is for child assessment, but it should feel like PLAY, not a test
- Describe what you actually see - be accurate
- If a child is shy, be extra gentle and encouraging
- Match their energy - if they're excited, be excited too!
- If they're quiet, be calm and patient
- Make every interaction feel like fun time with a friend!

**Your Super Powers:**
- You can see them through the camera (but make it sound magical, like "I can see you!")
- You understand when they're happy, sad, or excited (affective dialog)
- You know when to listen and when to talk (proactive audio)
- You wait for them to finish talking before you respond (turn detection)

Remember: You're Sparkle, and you're here to make children feel AMAZING and CONFIDENT while you observe and engage with them naturally!
""",
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-09-2025",
                voice="Aoede",
                temperature=0.9,
                # _gemini_tools=[types.GoogleSearch()],  # Commented out - web search disabled
            ),
        )

    async def on_enter(self):
        # Debug logging
        enable_recording_env = os.getenv("ENABLE_RECORDING", "not_set")
        logger.info(f"🎬 Agent entering room - Session: {self._session_id}")
        logger.info(f"🔍 DEBUG: ENABLE_RECORDING env var = '{enable_recording_env}'")
        logger.info(f"🔍 DEBUG: self._recording_enabled = {self._recording_enabled}")
        
        # Start recording in background (non-blocking)
        if self._recording_enabled:
            logger.info("✅ Recording is enabled - waiting for participants before recording")
            recording_task = asyncio.create_task(self._wait_and_record())
            self._tasks.append(recording_task)
            recording_task.add_done_callback(lambda t: self._tasks.remove(t))
        else:
            logger.warning(f"⚠️ Recording disabled - ENABLE_RECORDING='{enable_recording_env}'")
        
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
            
        get_job_context().room.register_byte_stream_handler("test", _image_received_handler)

        self.session.generate_reply(
            instructions="You are Sparkle! Greet the child warmly and introduce yourself as Sparkle, their fun new friend who can see them and is so excited to play together!"
        )
    
    async def on_exit(self):
        """Stop recording when agent leaves the room"""
        if self._egress_id:
            try:
                logger.info(f"🛑 Stopping recording: {self._egress_id}")
                async with aiohttp.ClientSession() as session:
                    egress_client = egress_service.EgressService(
                        session,
                        os.getenv("LIVEKIT_URL"),
                        os.getenv("LIVEKIT_API_KEY"),
                        os.getenv("LIVEKIT_API_SECRET"),
                    )
                    request = api.StopEgressRequest(egress_id=self._egress_id)
                    await egress_client.stop_egress(request)
                    logger.info(f"✅ Recording stopped successfully: {self._egress_id}")
            except Exception as e:
                logger.error(f"❌ Failed to stop recording: {e}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
    
    async def _wait_and_record(self):
        """
        Wait for participants to join, then start recording.
        Prevents "no tracks to record" error.
        """
        try:
            room = get_job_context().room
            logger.info("⏳ Waiting for participants to join before starting recording...")
            
            # Wait for at least one remote participant
            max_wait = 30  # seconds
            waited = 0
            while len(room.remote_participants) == 0 and waited < max_wait:
                await asyncio.sleep(0.5)
                waited += 0.5
            
            if len(room.remote_participants) == 0:
                logger.warning("⚠️ No participants joined within 30s, skipping recording")
                return
            
            logger.info(f"✅ Participant(s) detected: {len(room.remote_participants)}")
            logger.info("⏳ Waiting 2s for tracks to be published...")
            
            # Give tracks time to be published
            await asyncio.sleep(2.0)
            
            # Now start the recording
            await self._start_recording_safe()
            
        except Exception as e:
            logger.error(f"❌ Error in _wait_and_record: {e}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
    
    async def _start_recording_safe(self):
        """
        Start room recording with LiveKit Egress.
        - Stores on LiveKit Cloud (temporary 48h) OR AWS S3 (if configured)
        - Non-blocking: runs in background
        - Full error handling: never crashes the agent
        """
        room_name = get_job_context().room.name
        start_time = time.time()
        
        logger.info(f"🎥 RECORDING: Entered _start_recording_safe() for room: {room_name}")
        
        try:
            logger.info(f"📹 RECORDING: Starting recording for room: {room_name}")
            logger.info(f"🔑 RECORDING: Using credentials - URL: {os.getenv('LIVEKIT_URL')}")
            
            # Timeout protection - don't wait forever
            async with asyncio.timeout(15.0):
                # Create aiohttp session and egress client
                logger.info("🔌 RECORDING: Creating egress client...")
                async with aiohttp.ClientSession() as session:
                    egress_client = egress_service.EgressService(
                        session,
                        os.getenv("LIVEKIT_URL"),
                        os.getenv("LIVEKIT_API_KEY"),
                        os.getenv("LIVEKIT_API_SECRET"),
                    )
                    logger.info("✅ RECORDING: Egress client created")
                    
                    # Check if S3 is configured (optional for later)
                    use_s3 = (
                        os.getenv("AWS_ACCESS_KEY") and 
                        os.getenv("AWS_SECRET_KEY") and 
                        os.getenv("AWS_BUCKET_NAME")
                    )
                    
                    # Build request
                    if use_s3:
                        logger.info("☁️ RECORDING: Using AWS S3 storage")
                        request = api.RoomCompositeEgressRequest(
                            room_name=room_name,
                            layout="speaker",
                            file=api.EncodedFileOutput(
                                file_type=api.EncodedFileType.MP4,
                                filepath=f"sessions/{self._session_id}/{room_name}.mp4",
                                s3=api.S3Upload(
                                    access_key=os.getenv("AWS_ACCESS_KEY"),
                                    secret=os.getenv("AWS_SECRET_KEY"),
                                    region=os.getenv("AWS_REGION", "us-east-1"),
                                    bucket=os.getenv("AWS_BUCKET_NAME"),
                                )
                            )
                        )
                    else:
                        logger.info("⏱️ RECORDING: Using LiveKit Cloud temporary storage (48h retention)")
                        request = api.RoomCompositeEgressRequest(
                            room_name=room_name,
                            layout="speaker",
                            file=api.EncodedFileOutput(
                                file_type=api.EncodedFileType.MP4,
                                filepath=f"sessions/{self._session_id}/{room_name}.mp4"
                            )
                        )
                    
                    logger.info(f"📤 RECORDING: Sending request to LiveKit API...")
                    # Start the recording
                    info = await egress_client.start_room_composite_egress(request)
                    self._egress_id = info.egress_id
                    
                    duration = time.time() - start_time
                    logger.info(f"✅ RECORDING: Recording started successfully in {duration:.2f}s")
                    logger.info(f"   📊 RECORDING: Egress ID: {self._egress_id}")
                    logger.info(f"   📁 RECORDING: Filepath: sessions/{self._session_id}/{room_name}.mp4")
                    
                    if not use_s3:
                        logger.warning("⚠️ RECORDING: Using temporary storage - file will be deleted after 48h")
                
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.error(f"❌ RECORDING TIMEOUT: Failed after {duration:.2f}s")
            logger.error(f"   This usually means the egress service is not responding")
            self._egress_id = None
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ RECORDING FAILED: Error after {duration:.2f}s")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {str(e)}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.error(f"   Agent will continue normally without recording")
            self._egress_id = None
    
    async def _image_received(self, reader, participant_identity):
        logger.info("Received image from %s: '%s'", participant_identity, reader.info.name)
        try:
            image_bytes = bytes()
            async for chunk in reader:
                image_bytes += chunk

            chat_ctx = self.chat_ctx.copy()
            chat_ctx.add_message(
                role="user",
                content=[
                    ImageContent(
                        image=f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
                    )
                ],
            )
            await self.update_chat_ctx(chat_ctx)
            print("Image received", self.chat_ctx.copy().to_dict(exclude_image=False))
        except Exception as e:
            logger.error("Error processing image: %s", e)


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession()
    await session.start(
        agent=VisionAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))