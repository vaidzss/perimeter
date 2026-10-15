import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(Boolean);

  if (pathnames.length === 0) return null;

  return (
    <nav className="flex items-center gap-1.5 text-[12px] text-[#8B929C] mb-3 select-none">
      <Link to="/" className="hover:text-[#E6E8EB] transition-colors">
        Overview
      </Link>
      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={routeTo}>
            <ChevronRight className="w-3 h-3 text-[#5C626C]" strokeWidth={1.5} />
            {isLast ? (
              <span className="text-[#E6E8EB] font-normal">{name}</span>
            ) : (
              <Link to={routeTo} className="hover:text-[#E6E8EB] capitalize transition-colors">
                {name}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
