'use client';

import { useState } from 'react';
import ChallengeBuilder from '@/components/create/ChallengeBuilder';
import Link from 'next/link';

export default function CreatePage() {
  return (
    <div className="container max-w-4xl mx-auto px-4 py-12">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Create Challenge Set</h1>
          <p className="text-muted-foreground">
            Design custom DFA challenges for students. Generate a code to share with them.
          </p>
        </div>
        <Link 
          href="/"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          Return to Home
        </Link>
      </div>
      
      <div className="bg-card p-6 rounded-lg border">
        <ChallengeBuilder />
      </div>
    </div>
  );
} 