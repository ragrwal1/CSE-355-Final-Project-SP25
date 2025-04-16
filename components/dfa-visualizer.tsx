"use client"

import { useEffect, useMemo, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import type { DFA } from "@/lib/types"

interface DFAVisualizerProps {
  dfa: DFA
  showLabels?: boolean
  /**
   * String that will be streamed through the automaton. When it changes a new
   * animation cycle starts from the `start` state.
   */
  inputString?: string
  /** Diameter of the virtual circle on which states are laid out. */
  size?: number
}

/**
 * Beautiful, interactive DFA visualizer rendered with SVG.
 *
 * Features ▸ animated simulation ▸ hover‑highlighted transitions ▸ gentle
 * gradients ▸ elegant self‑loops ▸ responsive sizing.
 */
export default function DFAVisualizer({
  dfa,
  showLabels = true,
  inputString = "",
  size = 420,
}: DFAVisualizerProps) {
  /* ------------------------------------------------------------------ layout */
  const radius = size / 2 - 48 // leave a margin for arrowheads / labels
  const center = { x: size / 2, y: size / 2 }

  const statePositions = useMemo(() => {
    const n = dfa.states.length
    return Object.fromEntries(
      dfa.states.map((s, i) => {
        const angle = (2 * Math.PI * i) / n - Math.PI / 2 // start at 12 o'clock
        return [s, { x: center.x + radius * Math.cos(angle), y: center.y + radius * Math.sin(angle) }]
      }),
    ) as Record<string, { x: number; y: number }>
  }, [dfa.states, radius])

  /* -------------------------------------------------------------- simulation */
  const [cursor, setCursor] = useState(-1) // -1 ⇒ waiting
  const [current, setCurrent] = useState(dfa.start)

  // start over when input changes
  useEffect(() => {
    if (!inputString) {
      setCursor(-1)
      setCurrent(dfa.start)
      return
    }
    setCurrent(dfa.start)
    setCursor(0)
  }, [inputString, dfa.start])

  // drive the animation forward
  useEffect(() => {
    if (cursor < 0 || cursor >= inputString.length) return

    const id = setTimeout(() => {
      const sym = inputString[cursor]
      const nxt = dfa.transitions[current]?.[sym]
      setCurrent(nxt ?? current)
      setCursor((c) => c + 1)
    }, 900)

    return () => clearTimeout(id)
  }, [cursor, current, inputString, dfa.transitions])

  /* -------------------------------------------------------------- utilities */
  const mkEdgeId = (from: string, sym: string) => `${from}-${sym}-${dfa.transitions[from][sym]}`

  const edgePath = (
    from: { x: number; y: number },
    to: { x: number; y: number },
    self = false,
  ) => {
    const R = 28 // state circle radius
    if (self) {
      /* a gorgeous self‑loop drawn as a cubic Bézier */
      const off = 40
      return `M ${from.x} ${from.y - R} C ${from.x + off} ${from.y - R - off}, ${from.x - off} ${from.y - R - off}, ${from.x} ${from.y - R}`
    }
    // shorten path so it starts/ends exactly on state borders
    const dx = to.x - from.x
    const dy = to.y - from.y
    const len = Math.hypot(dx, dy)
    const ux = dx / len
    const uy = dy / len
    const start = { x: from.x + ux * R, y: from.y + uy * R }
    const end = { x: to.x - ux * R, y: to.y - uy * R }
    // simple straight path – curvature could be added here with quadratic‑curve offset
    return `M ${start.x} ${start.y} L ${end.x} ${end.y}`
  }

  /* ------------------------------------------------------------- rendering */
  return (
    <div className="w-full h-full flex items-center justify-center">
      <svg
        width="100%"
        viewBox={`0 0 ${size} ${size}`}
        xmlns="http://www.w3.org/2000/svg"
        className="max-w-full max-h-full select-none"
      >
        {/* ---- defs */}
        <defs>
          {/* arrowhead */}
          <marker
            id="arrow"
            viewBox="0 -5 10 10"
            refX="10"
            refY="0"
            markerWidth="8"
            markerHeight="8"
            orient="auto"
          >
            <path d="M0,-5 L10,0 L0,5 Z" className="fill-slate-500" />
          </marker>

          {/* glowing gradient for current state */}
          <radialGradient id="state-glow" fx="30%" fy="30%">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="100%" stopColor="#059669" />
          </radialGradient>
        </defs>

        {/* ---- transitions */}
        {dfa.states.flatMap((from) => {
          const transitions = dfa.transitions[from] ?? {}
          return Object.entries(transitions).map(([sym, to]) => {
            const self = from === to
            const path = edgePath(statePositions[from], statePositions[to], self)
            const id = mkEdgeId(from, sym)
            return (
              <g key={id}>
                <path
                  id={id}
                  d={path}
                  markerEnd="url(#arrow)"
                  className="stroke-slate-500 stroke-[2] fill-none transition-colors duration-200 hover:stroke-emerald-500"
                />
                {showLabels && (
                  <text className="text-sm fill-slate-700">
                    <textPath href={`#${id}`} startOffset="50%" textAnchor="middle">
                      {sym}
                    </textPath>
                  </text>
                )}
              </g>
            )
          })
        })}

        {/* ---- states */}
        {dfa.states.map((s) => {
          const { x, y } = statePositions[s]
          const isAccept = dfa.accept.includes(s)
          const isCurrent = s === current
          return (
            <g key={s}>
              {/* outer (accept) ring */}
              {isAccept && (
                <circle
                  cx={x}
                  cy={y}
                  r={32}
                  className="fill-none stroke-slate-700 stroke-[2]"
                />
              )}

              {/* main node */}
              <motion.circle
                initial={false}
                animate={{ r: 28 }}
                transition={{ type: "spring", stiffness: 160, damping: 12 }}
                cx={x}
                cy={y}
                r={28}
                className={
                  isCurrent
                    ? "shadow-2xl fill-[url(#state-glow)] stroke-emerald-800 stroke-[2]"
                    : "fill-white stroke-slate-700 stroke-[2]"
                }
              />

              {/* start indicator */}
              {s === dfa.start && (
                <path
                  d={`M ${x - 46} ${y} l 18 -8 v 16 z`}
                  className="fill-slate-700"
                />
              )}

              {/* label */}
              <text
                x={x}
                y={y}
                className="text-base font-medium fill-slate-800 select-none"
                dominantBaseline="central"
                textAnchor="middle"
              >
                {s}
              </text>
            </g>
          )
        })}

        {/* ---- overlay: input progress */}
        {inputString && (
          <AnimatePresence>
            {cursor <= inputString.length && cursor >= 0 && (
              <motion.text
                key="ticker"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                x={center.x}
                y={size - 16}
                dominantBaseline="central"
                textAnchor="middle"
                className="text-sm fill-slate-600"
              >
                reading “{inputString.slice(0, cursor)}▶{inputString.slice(cursor)}”
              </motion.text>
            )}
          </AnimatePresence>
        )}
      </svg>
    </div>
  )
}
