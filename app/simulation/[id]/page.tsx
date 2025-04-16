"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { ArrowLeft, Check, X } from "lucide-react"
import DFAVisualizer from "@/components/dfa-visualizer"
import { dfaData } from "@/lib/dfa-data"

export default function SimulationPage() {
  const [showLabels, setShowLabels] = useState(true)
  const [inputString, setInputString] = useState("")
  const [regexGuess, setRegexGuess] = useState("")
  const [isCorrectGuess, setIsCorrectGuess] = useState<boolean | null>(null)

  const handleSimulate = () => {
    // Reset any previous simulation state
    // The actual simulation is handled by the DFAVisualizer component
  }

  const handleGuessSubmit = () => {
    // Compare the guess with the actual regex
    setIsCorrectGuess(regexGuess === dfaData.regex)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex items-center">
          <Link href="/">
            <Button variant="outline" size="sm" className="mr-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">DFA Simulation</h1>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">DFA Visualization</h2>
            <div className="flex items-center space-x-2">
              <Switch id="labels-toggle" checked={showLabels} onCheckedChange={setShowLabels} />
              <Label htmlFor="labels-toggle">Show Labels</Label>
            </div>
          </div>

          <div className="h-[400px] border rounded-lg bg-slate-50 mb-6">
            <DFAVisualizer dfa={dfaData} showLabels={showLabels} inputString={inputString} />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">Simulate Input</h3>
              <div className="flex space-x-2">
                <Input
                  value={inputString}
                  onChange={(e) => setInputString(e.target.value)}
                  placeholder="Enter string (e.g., 'ab')"
                  className="flex-1"
                />
                <Button onClick={handleSimulate}>Simulate</Button>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-2">Guess the Regex</h3>
              <div className="flex space-x-2">
                <Input
                  value={regexGuess}
                  onChange={(e) => setRegexGuess(e.target.value)}
                  placeholder="Enter regex pattern"
                  className="flex-1"
                />
                <Button onClick={handleGuessSubmit}>Check</Button>
              </div>
              {isCorrectGuess !== null && (
                <div className={`mt-2 flex items-center ${isCorrectGuess ? "text-green-600" : "text-red-600"}`}>
                  {isCorrectGuess ? (
                    <>
                      <Check className="h-4 w-4 mr-1" />
                      <span>Correct!</span>
                    </>
                  ) : (
                    <>
                      <X className="h-4 w-4 mr-1" />
                      <span>Try again!</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
