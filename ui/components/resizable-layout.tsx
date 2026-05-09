'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface ResizableLayoutProps {
  left: React.ReactNode;
  right: React.ReactNode;
}

export function ResizableLayout({ left, right }: ResizableLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  // Motion value for width
  const width = useMotionValue(420);
  
  // Spring animation for smooth dragging feeling
  const springWidth = useSpring(width, {
    stiffness: 400,
    damping: 40,
    mass: 0.5,
  });

  const minWidth = 360;
  const maxWidth = 720;

  useEffect(() => {
    const handlePointerMove = (e: PointerEvent) => {
      if (!isDragging) return;
      if (!containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      let newWidth = e.clientX - containerRect.left;
      
      // Constraints
      if (newWidth < minWidth) newWidth = minWidth;
      if (newWidth > maxWidth) newWidth = maxWidth;
      
      width.set(newWidth);
    };

    const handlePointerUp = () => {
      setIsDragging(false);
      document.body.style.cursor = '';
    };

    if (isDragging) {
      window.addEventListener('pointermove', handlePointerMove);
      window.addEventListener('pointerup', handlePointerUp);
      document.body.style.cursor = 'col-resize';
    }

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      if (isDragging) document.body.style.cursor = '';
    };
  }, [isDragging, width]);

  return (
    <div ref={containerRef} className="flex flex-1 overflow-hidden relative">
      {/* Left Panel Wrapper */}
      <motion.div 
        style={{ width: springWidth }}
        className="flex-shrink-0 h-full overflow-hidden z-10"
      >
        {left}
      </motion.div>

      {/* Futuristic Divider */}
      <div 
        className="relative z-20 flex items-center justify-center -ml-1 -mr-1 w-2 cursor-col-resize group"
        onPointerDown={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Glow and Blur Background */}
        <motion.div
          animate={{
            opacity: isDragging || isHovered ? 1 : 0,
            width: isDragging || isHovered ? 24 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="absolute h-full bg-blue-500/10 blur-md pointer-events-none"
        />

        {/* Thin center glowing line */}
        <motion.div
          animate={{
            opacity: isDragging || isHovered ? 1 : 0.3,
            scaleX: isDragging ? 1.5 : 1,
            backgroundColor: isDragging ? '#3b82f6' : isHovered ? '#60a5fa' : '#ffffff',
          }}
          transition={{ duration: 0.2 }}
          className="h-full w-[1px] bg-white/30 transition-shadow duration-200"
          style={{ boxShadow: isDragging || isHovered ? '0 0 10px rgba(59, 130, 246, 0.8)' : 'none' }}
        />

        {/* Floating Handle */}
        <motion.div
          animate={{
            scale: isDragging ? 1.1 : isHovered ? 1 : 0.8,
            opacity: isDragging || isHovered ? 1 : 0,
          }}
          transition={{ duration: 0.2, type: 'spring', stiffness: 400, damping: 25 }}
          className="absolute flex h-10 w-4 items-center justify-center rounded-full border border-white/20 bg-black/80 backdrop-blur-md shadow-[0_0_15px_rgba(59,130,246,0.6)]"
        >
          <div className="flex -space-x-[2px]">
            <ChevronLeft className="h-3 w-3 text-white/70" />
            <ChevronRight className="h-3 w-3 text-white/70" />
          </div>
        </motion.div>
      </div>

      {/* Right Panel Wrapper */}
      <motion.div 
        className="flex-1 h-full overflow-hidden relative"
        animate={{
          scale: isDragging ? 0.99 : 1,
          opacity: isDragging ? 0.8 : 1,
        }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      >
        {right}
      </motion.div>
    </div>
  );
}
