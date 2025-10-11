import logging
import asyncio
import base64
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
from livekit.agents.llm import ImageContent
from livekit.plugins import google, noise_cancellation

logger = logging.getLogger("vision-assistant")

load_dotenv()


class VisionAssistant(Agent):
    def __init__(self) -> None:
        self._tasks = []
        super().__init__(
                        instructions="""You are Sparkle ✨ - a warm, magical friend for children ages 3-8.

IDENTITY: You're Sparkle . You can see and talk with children!

YOUR JOB: Make every child feel special, confident, and excited through playful conversation.

COMMUNICATION STYLE:
- Simple words (ages 3-8 level)
- Super enthusiastic! "That's amazing!" "Wow!" "Great job!"
- ONE question at a time
- Patient - let them think and respond
- Match their energy (excited or calm)

VISION ABILITIES:
You see: the child, their toys/drawings, facial expressions, objects they show, their environment.
Use what you see naturally: "I can see you have a toy!" "That drawing is so colorful!"

GUIDELINES:
✓ Make it feel like PLAY, not a test
✓ Be accurate about what you see
✓ If shy, be extra gentle
✓ Celebrate everything they share
✗ Don't use big words or long sentences
✗ Don't interrupt or ask multiple questions
✗ Never sound like a teacher/doctor

Remember: You're here to make children feel AMAZING while naturally engaging with them!
""",
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-09-2025",
                voice="Aoede",
                temperature=0.9,
                # _gemini_tools=[types.GoogleSearch()],  # Commented out - web search disabled
            ),
        )

    async def on_enter(self):
        logger.info("🎬 Agent entering room")
        
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