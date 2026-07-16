type FopMarkProps = {
  className?: string;
  title?: string;
};

export function FopMark({ className = "", title = "Fuzion platform F mark" }: FopMarkProps) {
  return (
    <svg className={className} viewBox="0 0 64 64" role="img" aria-label={title} xmlns="http://www.w3.org/2000/svg">
      <title>{title}</title>
      <path d="M14 10H52V22H28V30H47V42H28V54H14V10Z" fill="currentColor" />
    </svg>
  );
}
