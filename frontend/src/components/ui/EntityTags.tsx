/**
 * EntityTags — renders live extracted entities above the chat input.
 * Pass an array of { label, value, variant } to display tags.
 * Used for intent extraction, slot filling, or any live annotation.
 */

type Tag = {
  label?: string;
  value: string;
  variant?: string;
};

type Props = {
  tags: Tag[];
  loading?: boolean;
};

export function EntityTags({ tags, loading }: Props) {
  if (!loading && tags.length === 0) return null;

  return (
    <div className="entity-tags-row">
      {loading ? (
        <span className="tag tag--gray tag--pulse">
          <span className="tag-value">Analyzing…</span>
        </span>
      ) : (
        tags.map((t, i) => (
          <span key={i} className={`tag ${t.variant ?? "tag--gray"}`}>
            {t.label && <span className="tag-label">{t.label}</span>}
            <span className="tag-value">{t.value}</span>
          </span>
        ))
      )}
    </div>
  );
}
