type ErrorStateProps = {
  message: string;
  onRetry?: () => void;
};

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <section className="rounded-lg border border-rose-200 bg-rose-50 p-5">
      <h2 className="text-sm font-semibold text-rose-800">Unable to load Building Registry.</h2>
      <p className="mt-1 text-sm text-rose-700">{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 h-10 rounded-md bg-rose-700 px-4 text-sm font-semibold text-white"
        >
          Retry
        </button>
      ) : null}
    </section>
  );
}
