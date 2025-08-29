// src/components/ImageGrid.tsx
export function ImageGrid({ urls, alt }: { urls: string[]; alt: string }) {
    return (
      <div className="grid">
        {urls?.map((u,i) =>
          (u.startsWith("http") || u.startsWith("data:image"))
            ? <img key={i} src={u} alt={alt} loading="lazy"/>
            : <div key={i} className="tag">{String(u)}</div>
        )}
      </div>
    )
  }
  