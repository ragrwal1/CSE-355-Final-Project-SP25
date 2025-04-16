import React, { useState, useEffect } from 'react';
import { ChallengeSet, DFA } from '@/lib/types';
import { createChallengeSet, generateRandomDFA, getDFATemplates, DFAGenerationConfig, defaultPracticeConfig } from '@/lib/challengeService';
import DFAVisualizer from '@/components/dfa-visualizer';

const ChallengeBuilder: React.FC = () => {
  const [challengeName, setChallengeName] = useState('');
  const [challengeDescription, setChallengeDescription] = useState('');
  const [guessesPerProblem, setGuessesPerProblem] = useState(3);
  const [problems, setProblems] = useState<{ dfa: DFA, regex: string }[]>([]);
  const [generatedCode, setGeneratedCode] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [dfaTemplates, setDfaTemplates] = useState<{id: number, name: string}[]>([]);
  const [generationConfig, setGenerationConfig] = useState<DFAGenerationConfig>(defaultPracticeConfig);
  
  // For manual DFA input (simplified for this implementation)
  const [manualDfaInput, setManualDfaInput] = useState('');
  const [manualRegexInput, setManualRegexInput] = useState('');

  // Load DFA templates
  useEffect(() => {
    setDfaTemplates(getDFATemplates());
  }, []);
  
  const handleAddRandomDFA = () => {
    const randomDfa = generateRandomDFA(generationConfig);
    setProblems([...problems, { dfa: randomDfa, regex: randomDfa.regex }]);
  };
  
  const handleAddManualDFA = () => {
    try {
      // Very basic validation
      if (!manualDfaInput.trim() || !manualRegexInput.trim()) {
        alert('Please provide both DFA JSON and regex solution');
        return;
      }
      
      const dfaObj = JSON.parse(manualDfaInput);
      setProblems([...problems, { dfa: dfaObj, regex: manualRegexInput }]);
      
      // Clear inputs
      setManualDfaInput('');
      setManualRegexInput('');
    } catch (error) {
      alert('Invalid DFA JSON format');
    }
  };
  
  const handleRemoveProblem = (index: number) => {
    const updatedProblems = [...problems];
    updatedProblems.splice(index, 1);
    setProblems(updatedProblems);
  };
  
  const handleAlphabetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const alphabetStr = e.target.value.trim();
    if (!alphabetStr) return;
    
    // Convert the comma-separated string to an array and remove duplicates
    const alphabet = [...new Set(alphabetStr.split(',').map(char => char.trim()).filter(Boolean))];
    
    setGenerationConfig(prev => ({
      ...prev,
      alphabet
    }));
  };
  
  const handleComplexityChange = (complexity: 'easy' | 'medium' | 'hard') => {
    setGenerationConfig(prev => ({
      ...prev,
      complexity
    }));
  };
  
  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    
    if (value === 'random') {
      setGenerationConfig(prev => ({
        ...prev,
        templateIndex: undefined
      }));
    } else {
      setGenerationConfig(prev => ({
        ...prev,
        templateIndex: parseInt(value)
      }));
    }
  };
  
  const handleGenerateCode = async () => {
    if (problems.length === 0) {
      alert('Please add at least one problem');
      return;
    }
    
    setIsGenerating(true);
    
    try {
      const challengeData: Omit<ChallengeSet, 'id'> = {
        name: challengeName || 'Untitled Challenge',
        description: challengeDescription || 'No description provided',
        regexSolutions: problems.map(p => p.regex),
        dfas: problems.map(p => p.dfa),
        configs: {
          guessesPerProblem
        }
      };
      
      const generatedId = await createChallengeSet(challengeData);
      setGeneratedCode(generatedId);
    } catch (error) {
      alert('Error generating challenge code');
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h2 className="text-xl font-bold">Challenge Information</h2>
        
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="challenge-name" className="text-sm font-medium">Challenge Name</label>
            <input
              id="challenge-name"
              type="text"
              value={challengeName}
              onChange={(e) => setChallengeName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="e.g., Basic DFA Problems"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="guesses-per-problem" className="text-sm font-medium">Guesses Per Problem</label>
            <input
              id="guesses-per-problem"
              type="number"
              min={1}
              max={10}
              value={guessesPerProblem}
              onChange={(e) => setGuessesPerProblem(parseInt(e.target.value))}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <label htmlFor="challenge-description" className="text-sm font-medium">Description</label>
          <textarea
            id="challenge-description"
            value={challengeDescription}
            onChange={(e) => setChallengeDescription(e.target.value)}
            className="w-full px-3 py-2 border rounded-md min-h-[100px]"
            placeholder="Describe what this challenge set is about..."
          />
        </div>
      </div>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">Problems ({problems.length})</h2>
        </div>

        {/* DFA Generation Config */}
        <div className="p-4 border rounded-md bg-secondary/10 mb-6">
          <h3 className="text-lg font-semibold mb-4">Random DFA Generator</h3>
          
          <div className="grid gap-4 sm:grid-cols-2 mb-4">
            <div className="space-y-2">
              <label htmlFor="dfa-alphabet" className="text-sm font-medium">
                Alphabet (comma-separated)
              </label>
              <input
                id="dfa-alphabet"
                type="text"
                defaultValue={generationConfig.alphabet.join(',')}
                onChange={handleAlphabetChange}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="e.g., a,b,c"
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="dfa-template" className="text-sm font-medium">
                DFA Template
              </label>
              <select
                id="dfa-template"
                value={generationConfig.templateIndex !== undefined ? generationConfig.templateIndex.toString() : 'random'}
                onChange={handleTemplateChange}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="random">Random Template</option>
                {dfaTemplates.map(template => (
                  <option key={template.id} value={template.id.toString()}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="space-y-2 mb-4">
            <label className="text-sm font-medium">Complexity</label>
            <div className="flex gap-3">
              {(['easy', 'medium', 'hard'] as const).map(level => (
                <button
                  key={level}
                  onClick={() => handleComplexityChange(level)}
                  className={`px-3 py-1 rounded ${
                    generationConfig.complexity === level 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-secondary/50'
                  }`}
                  type="button"
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>
          
          <button
            onClick={handleAddRandomDFA}
            className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md"
            type="button"
          >
            Generate & Add Random DFA
          </button>
        </div>
        
        <div className="border-t pt-4">
          <h3 className="text-lg font-semibold mb-4">Manual DFA Input</h3>
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="manual-dfa" className="text-sm font-medium">DFA JSON</label>
              <textarea
                id="manual-dfa"
                value={manualDfaInput}
                onChange={(e) => setManualDfaInput(e.target.value)}
                className="w-full px-3 py-2 border rounded-md font-mono text-sm min-h-[150px]"
                placeholder='{"alphabet":["a","b"],"states":["q0","q1"],"start":"q0","accept":["q1"],"transitions":{"q0":{"a":"q0","b":"q1"},"q1":{"a":"q0","b":"q1"}}}'
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="manual-regex" className="text-sm font-medium">Regex Solution</label>
              <input
                id="manual-regex"
                type="text"
                value={manualRegexInput}
                onChange={(e) => setManualRegexInput(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="e.g., a*b+"
              />
            </div>
            
            <button
              onClick={handleAddManualDFA}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md"
              type="button"
            >
              Add Manual DFA
            </button>
          </div>
        </div>
        
        {problems.length > 0 && (
          <div className="space-y-4 mt-6">
            <h3 className="text-lg font-semibold">Added Problems</h3>
            <div className="grid gap-4 md:grid-cols-2">
              {problems.map((problem, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium">Problem {index + 1}</h4>
                    <button
                      onClick={() => handleRemoveProblem(index)}
                      className="text-red-500 hover:text-red-700"
                      type="button"
                    >
                      Remove
                    </button>
                  </div>
                  
                  <div className="h-32 border rounded bg-secondary/30 overflow-hidden">
                    <DFAVisualizer dfa={problem.dfa} />
                  </div>
                  
                  <div className="text-sm">
                    <span className="font-medium">Regex:</span>{' '}
                    <code className="font-mono bg-secondary/50 px-1 rounded">{problem.regex}</code>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div className="pt-6 border-t">
        <button
          onClick={handleGenerateCode}
          disabled={problems.length === 0 || isGenerating}
          className="w-full px-4 py-3 bg-primary text-primary-foreground rounded-md font-medium disabled:opacity-50"
          type="button"
        >
          {isGenerating ? 'Generating...' : 'Generate Challenge Code'}
        </button>
        
        {generatedCode && (
          <div className="mt-4 p-4 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-md">
            <p className="font-medium mb-2">Challenge Code Generated:</p>
            <div className="flex items-center gap-2">
              <code className="font-mono bg-white dark:bg-gray-800 px-2 py-1 rounded text-lg">{generatedCode}</code>
              <button
                onClick={() => {
                  if (navigator.clipboard) {
                    navigator.clipboard.writeText(generatedCode);
                    alert('Code copied to clipboard!');
                  }
                }}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                type="button"
              >
                Copy
              </button>
            </div>
            <p className="mt-2 text-sm">Share this code with students to access this challenge set.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChallengeBuilder; 