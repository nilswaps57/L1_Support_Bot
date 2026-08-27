import { ChatInput } from "../components/ChatInput";
import { ChatSessionControls } from "../components/ChatSessionControls";
import { MessageList } from "../components/MessageList";
import { useChatSession } from "../hooks/useChatSession";
import { Alert } from "../../../shared/components/Alert";
import { LoadingSkeleton } from "../../../shared/components/LoadingSkeleton";
import { PageHeader } from "../../../shared/components/PageHeader";
import styles from "./ChatPage.module.css";

export function ChatPage() {
  const { session, messages, sessionError, isLoading, isSending, send, clear, startNewSession, submitFeedback } = useChatSession();

  return (
    <main className={`appContainer ${styles.page}`}>
      <PageHeader title="Chat" description="FLEXCUBE support for branch users." />
      <ChatSessionControls expiresAt={session?.expires_at} onClear={() => void clear()} disabled={isLoading || isSending} />
      {sessionError ? (
        <div className={styles.sessionError}>
          <Alert tone="error">{sessionError}</Alert>
          <div>
            <button type="button" onClick={() => void startNewSession()}>Start new session</button>
          </div>
        </div>
      ) : null}
      <section className={styles.conversationFrame} aria-label="Conversation workspace">
        {isLoading && !session ? <LoadingSkeleton variant="conversation" label="Preparing chat session" /> : null}
        {!isLoading ? (
          <MessageList
            messages={messages}
            pending={isSending}
            onFeedback={(answerId, rating, comment) => submitFeedback(answerId, rating, comment)}
          />
        ) : null}
      </section>
      <section className={styles.composerFrame} aria-label="Question composer">
        <ChatInput onSubmit={(question) => void send(question)} disabled={isLoading || isSending || !session} />
      </section>
    </main>
  );
}
