// src/components/Dayboard.tsx
import { TagList } from "./TagList"
import { ImageGrid } from "./ImageGrid"
import type { Dayboard } from "../types"

export function DayboardView({ data }: { data: Dayboard }) {
  return (
    <section className="card">
      <div className="row" style={{justifyContent:"space-between"}}>
        <h2 style={{margin:0}}>Your Dayboard</h2>
        <span className="pill small">Mood: <strong>{data.mood_word}</strong></span>
      </div>

      <div className="divider" />

      <div className="result-grid">
        <div>
          <span className="pill">☕ <strong className="coffee">{data.coffee}</strong></span>
          <div className="divider" />
          <h3 className="small" style={{color:"var(--muted)"}}>Songs</h3>
          <TagList items={data.songs} icon="🎵" />
          <div className="divider" />
          <h3 className="small" style={{color:"var(--muted)"}}>Outfits</h3>
          <TagList items={data.outfits} icon="👗" />
        </div>
        <div>
          <ImageGrid urls={data.images} alt={data.mood_word} />
        </div>
      </div>
    </section>
  )
}
