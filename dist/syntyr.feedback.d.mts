/** Small optional Clipboard API and live-status enhancement. */
export declare function announceFeedback(
  status: Element | null | undefined,
  message: string,
  options?: { duration?: number }
): boolean;
export declare function enhanceFeedback(root?: Document | Element): () => void;
