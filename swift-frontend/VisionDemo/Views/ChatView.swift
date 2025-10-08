import LiveKit
import LiveKitComponents
import SwiftUI

struct ChatView: View {
    @EnvironmentObject var chatContext: ChatContext
    @EnvironmentObject var room: Room
    @State private var animateActionBar = false

    var body: some View {
        ZStack(alignment: room.localParticipant.isCameraEnabled() ? .top : .center) {
            // Show loading state while waiting for agent
            if chatContext.agentParticipant == nil {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.5)
                        .padding(.bottom, 8)
                    
                    Text("Connecting to AI assistant...")
                        .font(.headline)
                    
                    Text("First connection may take 10-20 seconds")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            }
            
            VStack(alignment: .center) {
                Spacer()

                CameraView()
                    .frame(
                        width: CGFloat(chatContext.cameraDimensions.width) / screenScale(),
                        height: CGFloat(chatContext.cameraDimensions.height) / screenScale()
                    )
                    .opacity(room.localParticipant.isCameraEnabled() ? 1 : 0)
                    .animation(.snappy, value: room.localParticipant.isCameraEnabled())

                ActionBarView()
                    .opacity(animateActionBar ? 1 : 0)
                    .offset(y: animateActionBar ? 0 : 10)
                    .animation(.easeOut(duration: 0.2), value: animateActionBar)
                    .onAppear {
                        animateActionBar = true
                    }
            }
            .opacity(chatContext.agentParticipant == nil ? 0 : 1)

            AgentView()
                .frame(
                    width: agentSize().width,
                    height: agentSize().height
                )
                .offset(y: room.localParticipant.isCameraEnabled() ? 0 : -40)
                .animation(.snappy, value: room.localParticipant.isCameraEnabled())
        }
    }

    private func screenScale() -> CGFloat {
        #if os(visionOS)
        return 1
        #else
        return UIScreen.main.scale
        #endif
    }

    private func agentSize() -> CGSize {
        #if os(visionOS)
        return CGSize(width: 100, height: 100)
        #else
        return CGSize(
        width: room.localParticipant.isCameraEnabled() ? 100 : UIScreen.main.bounds.size.width - 64,
        height: room.localParticipant.isCameraEnabled() ? 100 : UIScreen.main.bounds.size.width - 64
        )
        #endif
    }
}
