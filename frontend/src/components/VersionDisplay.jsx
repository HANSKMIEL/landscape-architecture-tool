import { useEffect, useState } from 'react';

/**
 * VersionDisplay Component
 * Fetches and displays version information from the backend health endpoint
 * Shows branch info for development deployments
 */
const VersionDisplay = ({ className = '' }) => {
  const [versionInfo, setVersionInfo] = useState({
    version: 'Loading...',
    branch: null,
    environment: null
  });

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const response = await fetch('/health');
        if (response.ok) {
          const data = await response.json();
          setVersionInfo({
            version: data.version || '2.0.0',
            branch: data.branch || null,
            environment: data.environment || null
          });
        } else {
          // Fallback to package.json version
          setVersionInfo({
            version: '2.0.0',
            branch: null,
            environment: null
          });
        }
      } catch (error) {
        console.error('Failed to fetch version:', error);
        setVersionInfo({
          version: '2.0.0',
          branch: null,
          environment: null
        });
      }
    };

    fetchVersion();
  }, []);

  // Determine display text based on environment
  const getVersionText = () => {
    if (versionInfo.environment === 'production' && versionInfo.branch) {
      return `v${versionInfo.version} (${versionInfo.branch})`;
    }
    return `v${versionInfo.version}`;
  };

  // Determine styling based on environment
  const getVersionStyle = () => {
    if (versionInfo.branch === 'V1.00D' || versionInfo.environment === 'development') {
      return 'text-orange-600 font-semibold';
    }
    return 'text-gray-400';
  };

  return (
    <div className={`text-xs ${getVersionStyle()} ${className}`}>
      {getVersionText()}
      {versionInfo.branch === 'V1.00D' && (
        <span className="ml-1 text-[10px] bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded">
          DEV
        </span>
      )}
    </div>
  );
};

export default VersionDisplay;
