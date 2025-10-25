'use client';

import { useState } from 'react';
import { SearchPage } from '@/components/SearchPage';
import { MemoryPage } from '@/components/MemoryPage';

export default function Home() {
  const [currentPage, setCurrentPage] = useState<'search' | 'memory'>('search');
  const [selectedPhoto, setSelectedPhoto] = useState<any>(null);

  const handleShowMemory = (photo: any) => {
    setSelectedPhoto(photo);
    setCurrentPage('memory');
  };

  const handleBackToSearch = () => {
    setCurrentPage('search');
    setSelectedPhoto(null);
  };

  return (
    <main className="min-h-screen bg-black">
      {currentPage === 'search' ? (
        <SearchPage onShowMemory={handleShowMemory} />
      ) : (
        <MemoryPage photo={selectedPhoto} onBack={handleBackToSearch} />
      )}
    </main>
  );
}
