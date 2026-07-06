type ErrorStateProps = {
  message: string;
  onRetry?: () => void;
};

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <section className="rounded-2xl border border-red-200 bg-red-50 p-5">
      <h2 className="text-sm font-semibold text-red-700">Unable to load this workspace.</h2>
      <p className="mt-1 text-sm text-red-600">{message}</p>
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
