type ErrorStateProps = {
  message: string;
  onRetry?: () => void;
};

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <section className="rounded-2xl border border-red-400/25 bg-red-500/10 p-5">
      <h2 className="text-sm font-semibold text-red-200">Unable to load this workspace.</h2>
      <p className="mt-1 text-sm text-red-100/80">{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="fop-button-secondary mt-4 h-10"
        >
          Retry
        </button>
      ) : null}
    </section>
  );
}
