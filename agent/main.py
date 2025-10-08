import logging
import asyncio
import base64
from pyexpat import model
from dotenv import load_dotenv
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
        super().__init__(
            instructions="""
You are an advanced AI vision assistant with real-time voice interaction. Your primary functions include:

1. **Visual Analysis**: You can receive and analyze images or screen captures from users. When you receive an image, carefully examine it and provide detailed, accurate descriptions or answer specific questions about what you see.

2. **Voice Interaction**: You communicate through natural, conversational voice responses. Be concise yet informative, and maintain a friendly, professional tone.

3. **Real-time Assistance**: You operate in real-time sessions, so provide immediate, contextually relevant responses. Remember the conversation history and refer back to previous images or topics when relevant.

4. **Capabilities**:
   - Identify objects, text, people, and scenes in images
   - Read and interpret text from screenshots or documents
   - Analyze UI/UX elements and provide feedback
   - Assist with visual problem-solving and troubleshooting
   - Answer questions about visual content with precision

5. **Communication Style**:
   - Be direct and clear in your responses
   - Ask clarifying questions if the user's intent is unclear
   - Proactively offer insights about visual content
   - Adapt your level of detail based on the user's needs

Always prioritize accuracy over speed, and admit when you're uncertain about visual details rather than guessing.""",
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-09-2025",
                voice="Aoede",
                temperature=0.9,
                # _gemini_tools=[types.GoogleSearch()],  # Commented out - web search disabled
            ),
        )

    async def on_enter(self):
        def _image_received_handler(reader, participant_identity):
            task = asyncio.create_task(
                self._image_received(reader, participant_identity)
            )
            self._tasks.append(task)
            task.add_done_callback(lambda t: self._tasks.remove(t))
            
        get_job_context().room.register_byte_stream_handler("test", _image_received_handler)

        self.session.generate_reply(
            instructions="Briefly greet the user and offer your assistance."
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
# Test change
