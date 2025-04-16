'use client'

import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from 'next/navigation'
import { getRecentChallengeCodes, saveRecentChallengeCode } from '@/lib/challengeService'

export default function Home() {
  const [challengeCode, setChallengeCode] = useState("")
  const [recentCodes, setRecentCodes] = useState<string[]>([])
  const [isClient, setIsClient] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Ensure localStorage is accessed only on the client side
    setIsClient(true)
  }, [])

  useEffect(() => {
    // Load recent codes from localStorage on client
    if (isClient) {
      const codes = getRecentChallengeCodes()
      setRecentCodes(codes)
    }
  }, [isClient])

  const handleStartChallenge = (code: string) => {
    if (!code.trim()) {
      alert('Please enter a challenge code')
      return
    }
    
    // Save the code to localStorage
    saveRecentChallengeCode(code)
    
    // Update the UI list
    if (!recentCodes.includes(code)) {
      setRecentCodes([...recentCodes, code])
    }
    
    // Navigate to the challenge page
    router.push(`/challenge/${code}`)
  }
  
  const handleRemoveCode = (codeToRemove: string, e: React.MouseEvent) => {
    e.stopPropagation()
    
    // Remove from state and localStorage
    const updatedCodes = recentCodes.filter(code => code !== codeToRemove)
    setRecentCodes(updatedCodes)
    localStorage.setItem('recent_challenge_codes', JSON.stringify(updatedCodes))
  }

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-16">
        <header className="mb-16 text-center">
          <h1 className="text-4xl font-bold mb-4">
            Interactive DFA/Regex Practice Tool
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Convert DFAs to Regular Expressions with this interactive tool. Enter a challenge code or try the infinite practice mode.
          </p>
        </header>

        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-12">
          {/* Challenge Code Section */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Enter Challenge Code</h2>
              <p className="text-muted-foreground">
                Start a specific challenge set by entering the code provided by your instructor.
              </p>
              
              <div className="flex gap-3">
                <input
                  type="text"
                  value={challengeCode}
                  onChange={(e) => setChallengeCode(e.target.value)}
                  placeholder="e.g., DFA101"
                  className="flex-1 px-3 py-2 border rounded-md"
                />
                <button
                  onClick={() => handleStartChallenge(challengeCode)}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
                >
                  Start Challenge
                </button>
              </div>
            </div>
            
            {isClient && recentCodes.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-medium">Recent Challenges</h3>
                <ul className="space-y-2">
                  {recentCodes.map((code) => (
                    <li 
                      key={code}
                      onClick={() => handleStartChallenge(code)}
                      className="flex justify-between items-center p-3 bg-secondary/50 rounded-md cursor-pointer hover:bg-secondary/70"
                    >
                      <span className="font-medium">{code}</span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => handleRemoveCode(code, e)}
                          className="text-sm text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          {/* Other Modes Section */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Infinite Practice Mode</h2>
              <p className="text-muted-foreground">
                Generate random DFA/Regex problems for unlimited practice.
              </p>
              <Link
                href="/practice"
                className="block w-full px-4 py-3 bg-secondary text-secondary-foreground text-center rounded-md font-medium"
              >
                Start Practice Mode
              </Link>
            </div>
            
            <div className="pt-8 border-t">
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold">For Instructors</h2>
                <p className="text-muted-foreground">
                  Create custom challenge sets with specific DFA problems for your students.
                </p>
                <Link
                  href="/create"
                  className="block w-full px-4 py-3 border border-primary text-primary hover:bg-primary/10 text-center rounded-md font-medium"
                >
                  Create Challenge Set
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="max-w-5xl mx-auto mt-16 pt-10 border-t">
          <h2 className="text-2xl font-semibold mb-6 text-center">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-card p-6 rounded-lg border">
              <h3 className="font-medium text-lg mb-2">1. Enter Code or Practice</h3>
              <p className="text-muted-foreground">
                Enter a challenge code provided by your instructor or start the infinite practice mode.
              </p>
            </div>
            <div className="bg-card p-6 rounded-lg border">
              <h3 className="font-medium text-lg mb-2">2. Analyze the DFA</h3>
              <p className="text-muted-foreground">
                Study the visual representation of the Deterministic Finite Automaton (DFA).
              </p>
            </div>
            <div className="bg-card p-6 rounded-lg border">
              <h3 className="font-medium text-lg mb-2">3. Convert to Regex</h3>
              <p className="text-muted-foreground">
                Enter your regular expression solution and get immediate feedback.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
