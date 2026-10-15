import React from 'react';

interface CornerBracketsProps {
  children: React.ReactNode;
  className?: string;
  borderColor?: string;
  cornerSize?: number;
}

export const CornerBrackets: React.FC<CornerBracketsProps> = ({
  children,
  className = '',
  borderColor = '#6B7A83',
  cornerSize = 8,
}) => {
  return (
    <div className={`relative ${className}`}>
      {/* Top Left */}
      <span
        className="absolute pointer-events-none"
        style={{
          top: -1,
          left: -1,
          width: cornerSize,
          height: cornerSize,
          borderTop: `1px solid ${borderColor}`,
          borderLeft: `1px solid ${borderColor}`,
          zIndex: 10,
        }}
      />
      {/* Top Right */}
      <span
        className="absolute pointer-events-none"
        style={{
          top: -1,
          right: -1,
          width: cornerSize,
          height: cornerSize,
          borderTop: `1px solid ${borderColor}`,
          borderRight: `1px solid ${borderColor}`,
          zIndex: 10,
        }}
      />
      {/* Bottom Left */}
      <span
        className="absolute pointer-events-none"
        style={{
          bottom: -1,
          left: -1,
          width: cornerSize,
          height: cornerSize,
          borderBottom: `1px solid ${borderColor}`,
          borderLeft: `1px solid ${borderColor}`,
          zIndex: 10,
        }}
      />
      {/* Bottom Right */}
      <span
        className="absolute pointer-events-none"
        style={{
          bottom: -1,
          right: -1,
          width: cornerSize,
          height: cornerSize,
          borderBottom: `1px solid ${borderColor}`,
          borderRight: `1px solid ${borderColor}`,
          zIndex: 10,
        }}
      />
      {children}
    </div>
  );
};
