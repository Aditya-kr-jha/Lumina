import { Check, X } from 'lucide-react';

const PasswordStrengthIndicator = ({ password, showRequirements = true }) => {
  const calculateStrength = (password) => {
    let score = 0;
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      numbers: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    // Calculate score
    if (requirements.length) score += 20;
    if (requirements.uppercase) score += 20;
    if (requirements.lowercase) score += 20;
    if (requirements.numbers) score += 20;
    if (requirements.special) score += 20;

    // Bonus for longer passwords
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 10;

    return { score, requirements };
  };

  const getStrengthInfo = (score) => {
    if (score < 20) return { level: 0, label: '', color: 'bg-gray-200' };
    if (score < 40) return { level: 1, label: 'Weak', color: 'bg-red-500' };
    if (score < 70) return { level: 2, label: 'Medium', color: 'bg-yellow-500' };
    if (score < 90) return { level: 3, label: 'Strong', color: 'bg-blue-500' };
    return { level: 4, label: 'Very Strong', color: 'bg-green-500' };
  };

  const { score, requirements } = calculateStrength(password);
  const strengthInfo = getStrengthInfo(score);

  if (!password) return null;

  return (
    <div className="mt-2 space-y-2">
      {/* Progress Bar */}
      <div className="space-y-1">
        <div className="flex gap-1">
          {[1, 2, 3, 4].map((level) => (
            <div
              key={level}
              className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${
                level <= strengthInfo.level
                  ? strengthInfo.color
                  : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        
        {strengthInfo.label && (
          <p className={`text-xs font-medium ${
            strengthInfo.level === 1 ? 'text-red-600' :
            strengthInfo.level === 2 ? 'text-yellow-600' :
            strengthInfo.level === 3 ? 'text-blue-600' :
            strengthInfo.level === 4 ? 'text-green-600' : 'text-gray-600'
          }`}>
            {strengthInfo.label}
          </p>
        )}
      </div>

      {/* Requirements List */}
      {showRequirements && (
        <div className="space-y-1">
          {Object.entries(requirements).map(([key, met]) => (
            <div key={key} className="flex items-center gap-2 text-xs">
              {met ? (
                <Check className="text-green-500" size={12} />
              ) : (
                <X className="text-gray-400" size={12} />
              )}
              <span className={met ? 'text-green-700' : 'text-gray-500'}>
                {key === 'length' && 'At least 8 characters'}
                {key === 'uppercase' && 'Contains uppercase letter'}
                {key === 'lowercase' && 'Contains lowercase letter'}
                {key === 'numbers' && 'Contains number'}
                {key === 'special' && 'Contains special character'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PasswordStrengthIndicator;
