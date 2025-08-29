// src/components/MoodForm.tsx
import { useState } from "react"
export function MoodForm({ onSubmit }: { onSubmit: (mood: string) => void }) {
  const [mood, setMood] = useState("")
  const send = () => mood.trim() && onSubmit(mood.trim())
  const pick = (w: string) => { setMood(w); onSubmit(w) }
  return (
    <section className="card" aria-labelledby="moodFormTitle">
      <h2 id="moodFormTitle" style={{margin:"0 0 8px 0", fontSize:18, color:"var(--muted)"}}>
        Describe your mood
      </h2>
      <label htmlFor="mood">One word</label>
      <div className="row">
        <input id="mood" value={mood}
          placeholder="happy, sad, chill, ..."
          onChange={e=>setMood(e.target.value)}
          onKeyDown={e=>e.key==="Enter" && send()} />
        <button onClick={send}>Create Dayboard</button>
      </div>
      <div className="mood-choices" aria-label="Quick choices">
        {["happy","chill","sad","focused","confident"].map(w=>(
          <span key={w} className="chip" onClick={()=>pick(w)}>{w}</span>
        ))}
      </div>
    </section>
  )
}
