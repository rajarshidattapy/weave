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
        {/* Minimal sleek line */}
        <motion.div
          animate={{
            backgroundColor: isDragging ? 'rgba(255, 255, 255, 0.4)' : isHovered ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            width: isDragging || isHovered ? 2 : 1,
          }}
          transition={{ duration: 0.15 }}
          className="h-full"
        />
      </div>

      {/* Right Panel Wrapper */}
      <motion.div 
        className="flex-1 flex flex-col h-full overflow-hidden relative"
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
