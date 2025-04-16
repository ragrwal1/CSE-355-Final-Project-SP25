'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Code, PlusCircle, BookOpen, User, GraduationCap } from "lucide-react"
import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

interface Challenge {
  id: string
  code: string
  name: string
  className: string
  teacher: string
}

export default function Home() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [challengeCode, setChallengeCode] = useState("")
  const [isClient, setIsClient] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  useEffect(() => {
    // Ensure localStorage is accessed only on the client side
    setIsClient(true)
    const storedChallenges = localStorage.getItem("addedChallenges")
    if (storedChallenges) {
      setChallenges(JSON.parse(storedChallenges))
    }
  }, [])

  useEffect(() => {
    // Update localStorage whenever challenges change, only on client side
    if (isClient) {
      localStorage.setItem("addedChallenges", JSON.stringify(challenges))
    }
  }, [challenges, isClient])

  const handleAddChallenge = () => {
    if (!challengeCode.trim()) return // Basic validation

    const newChallenge: Challenge = {
      id: crypto.randomUUID(), // Simple unique ID
      code: challengeCode.trim(),
      // Placeholder details - replace with actual data fetching if needed later
      name: `Challenge ${challengeCode.substring(0, 5)}...`,
      className: "CSE 355",
      teacher: "Prof. Example",
    }

    setChallenges((prevChallenges) => [...prevChallenges, newChallenge])
    setChallengeCode("") // Reset input field
    setIsDialogOpen(false) // Close dialog
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <header className="mb-16 text-center">
          <h1 className="text-5xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400 tracking-tight">
            Interactive DFA Challenges
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
            Add challenge codes provided by your instructor, visualize the DFA, and test your regex skills.
          </p>
        </header>

        {/* Add Challenge Button and Dialog */}
        <div className="flex justify-center mb-12">
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-full shadow-lg transition-transform transform hover:scale-105">
                <PlusCircle className="mr-2 h-5 w-5" />
                Add New Challenge
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] bg-white dark:bg-gray-800 rounded-lg shadow-xl">
              <DialogHeader>
                <DialogTitle className="text-slate-900 dark:text-white">Add Challenge Code</DialogTitle>
                <DialogDescription className="text-slate-600 dark:text-slate-400">
                  Enter the unique code for the challenge you want to add.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="challenge-code" className="text-right text-slate-700 dark:text-slate-300">
                    Code
                  </Label>
                  <Input
                    id="challenge-code"
                    value={challengeCode}
                    onChange={(e) => setChallengeCode(e.target.value)}
                    className="col-span-3 bg-slate-100 dark:bg-gray-700 border-slate-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500 dark:text-white"
                    placeholder="Enter challenge code"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  onClick={handleAddChallenge}
                  className="bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-500 dark:hover:bg-blue-600"
                >
                  Add Challenge
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Added Challenges Section */}
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-slate-800 dark:text-slate-200 text-center">Added Challenges</h2>
          {isClient && challenges.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {challenges.map((challenge) => (
                <Card key={challenge.id} className="bg-white dark:bg-gray-800 shadow-lg rounded-xl overflow-hidden hover:shadow-xl transition-shadow duration-300 flex flex-col">
                  <CardHeader className="bg-slate-50 dark:bg-gray-700 p-4">
                    <CardTitle className="text-lg font-semibold text-slate-900 dark:text-white flex items-center">
                      <BookOpen className="mr-2 h-5 w-5 text-blue-500 dark:text-blue-400" />
                      {challenge.name}
                    </CardTitle>
                    <CardDescription className="text-sm text-slate-500 dark:text-slate-400">Code: {challenge.code}</CardDescription>
                  </CardHeader>
                  <CardContent className="p-4 space-y-2 flex-grow">
                     <div className="flex items-center text-sm text-slate-600 dark:text-slate-300">
                       <GraduationCap className="mr-2 h-4 w-4 text-purple-500 dark:text-purple-400"/> Class: {challenge.className}
                     </div>
                     <div className="flex items-center text-sm text-slate-600 dark:text-slate-300">
                       <User className="mr-2 h-4 w-4 text-pink-500 dark:text-pink-400"/> Teacher: {challenge.teacher}
                     </div>
                  </CardContent>
                  <CardFooter className="bg-slate-50 dark:bg-gray-700 p-4 flex justify-end">
                    <Link href={`/simulation/${challenge.id}`} passHref>
                       <Button className="bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white text-sm transition-transform transform hover:scale-105">
                        <Code className="mr-2 h-4 w-4" />
                        Enter Challenge
                      </Button>
                    </Link>
                  </CardFooter>
                </Card>
              ))}
            </div>
          ) : (
             isClient && (
                <div className="text-center text-slate-500 dark:text-slate-400 py-10 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                    <p className="mb-4">No challenges added yet.</p>
                    <p>Click the "Add New Challenge" button above to get started!</p>
                 </div>
             )
          )}
           {/* Render placeholder or loading state server-side / before hydration */}
           {!isClient && (
             <div className="text-center text-slate-500 dark:text-slate-400 py-10">Loading challenges...</div>
           )}
        </div>

        {/* How it works Section (Optional - kept for context) */}
        <div className="max-w-4xl mx-auto mt-16 pt-10 border-t border-slate-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold mb-6 text-slate-800 dark:text-slate-200 text-center">How Challenges Work</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transform hover:scale-105 transition-transform duration-300">
              <h3 className="font-medium text-lg mb-2 text-slate-900 dark:text-white">1. Add Code</h3>
              <p className="text-slate-600 dark:text-slate-400">
                Use the "Add New Challenge" button and enter the code provided by your instructor.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transform hover:scale-105 transition-transform duration-300">
              <h3 className="font-medium text-lg mb-2 text-slate-900 dark:text-white">2. Enter Challenge</h3>
              <p className="text-slate-600 dark:text-slate-400">
                Click "Enter Challenge" on the card to load the specific DFA visualization and simulation.
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm transform hover:scale-105 transition-transform duration-300">
              <h3 className="font-medium text-lg mb-2 text-slate-900 dark:text-white">3. Learn & Solve</h3>
              <p className="text-slate-600 dark:text-slate-400">
                Interact with the DFA, test strings, understand its behavior, and try to guess the associated regex.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
