import SwiftUI

struct ConnectionView: View {
    @EnvironmentObject private var chatContext: ChatContext

    @State private var isConnecting: Bool = false
    @State private var errorMessage: String = ""
    private var tokenService: TokenService = .init()

    var body: some View {
        if chatContext.isConnected {
            ChatView()
        } else {
            VStack(spacing: 24) {
                Text("JLAIS Vision Demo")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text(
                    "Talk to the JLAIS"
                )
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal)

                Button(action: {
                    Task {
                        isConnecting = true

                        let roomName = "test-room"//''"room-\(Int.random(in: 1000 ... 9999))"
                        let participantName = "user-\(Int.random(in: 1000 ... 9999))"

                        do {
                            print("🔵 Starting connection...")
                            if let connectionDetails = try await tokenService.fetchConnectionDetails(
                                roomName: roomName,
                                participantName: participantName
                            ) {
                                print("✅ Got connection details")
                                print("Server URL: \(connectionDetails.serverUrl)")
                                try await chatContext.connect(
                                    url: connectionDetails.serverUrl,
                                    token: connectionDetails.participantToken
                                )
                                print("✅ Connected successfully")
                            } else {
                                let msg = "Failed to fetch connection details - check sandbox ID"
                                print("❌ \(msg)")
                                errorMessage = msg
                            }
                        } catch {
                            let msg = "Connection error: \(error.localizedDescription)"
                            print("❌ \(msg)")
                            errorMessage = msg
                        }
                        isConnecting = false
                    }
                }) {
                    Text(isConnecting ? "Connecting..." : "Connect")
                        .font(.headline)
                        .frame(maxWidth: 280)
                        .animation(.none, value: isConnecting)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .disabled(isConnecting)
                
                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
            }
            .padding()
        }
    }
}
