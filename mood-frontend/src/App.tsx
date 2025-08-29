// src/App.tsx
import { useEffect, useState } from "react"
import { MoodForm } from "./components/MoodForm"
import { DayboardView } from "./components/Dayboard"
import type { Dayboard } from "./types"

const moodAccent: Record<string,string> = {
  happy:"#f6c453", chill:"#6ee7b7", sad:"#93c5fd", focused:"#f472b6", confident:"#fde047"
}
function setAccent(color: string) {
  document.documentElement.style.setProperty("--accent", color)
  const c = color.replace("#",""); const r=parseInt(c.slice(0,2),16), g=parseInt(c.slice(2,4),16), b=parseInt(c.slice(4,6),16)
  document.documentElement.style.setProperty("--ring", `rgba(${r},${g},${b},.35)`)
}

export default function App() {
  const [data, setData] = useState<Dayboard | null>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!data?.mood_word) return
    setAccent(moodAccent[data.mood_word.toLowerCase()] ?? "#6ee7b7")
  }, [data?.mood_word])

  async function createDayboard(mood: string) {
    setLoading(true); setErr(null)
    try {
      const r = await fetch("/dayboard", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ mood_word: mood })
      })
      if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
      const j = await r.json() as Dayboard
      setData({ ...j, mood_word: j.mood_word || mood })
    } catch(e:any) {
      setErr(e?.message || "Request failed")
    } finally { setLoading(false) }
  }

  return (
    <div className="wrap">
      <header>
        <div className="brand"><div className="logo" /><h1>Mood Dayboard</h1></div>
        <span className="pill small">{loading ? "Loading…" : err ? "Error" : "Ready"}</span>
      </header>

      <MoodForm onSubmit={createDayboard} />
      {err && <div className="card hint" style={{color:"#fca5a5"}}>{err}</div>}
      {data && <DayboardView data={data} />}
    </div>
  )
}
