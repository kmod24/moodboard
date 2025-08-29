// src/components/TagList.tsx
export function TagList({ items, icon }: { items: string[]; icon?: string }) {
    return (
      <div className="tags">
        {items?.map((t,i)=><span key={i} className="tag">{icon} {t}</span>)}
      </div>
    )
  }
  