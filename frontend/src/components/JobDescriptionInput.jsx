import React, { useState } from 'react';

const JobDescriptionInput = ({ value, onChange, onSubmit, error }) => {
  const [charCount, setCharCount] = useState(value ? value.length : 0);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setCharCount(newValue.length);
    onChange(newValue);
  };

  return (
    <div className="space-y-4">
      <label htmlFor="job-description" className="block text-sm font-medium text-gray-700">
        Job Description
      </label>
      <textarea
        id="job-description"
        rows={6}
        className="w-full border rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Paste the job description here..."
        value={value}
        onChange={handleChange}
      />
      <div className="flex justify-between text-xs text-gray-500">
        <span>{charCount} characters</span>
        <span>Min 50, Max 5000</span>
      </div>
      {error && <div className="text-red-500 text-xs">{error}</div>}
      <button
        className="btn-primary px-4 py-2 rounded"
        onClick={onSubmit}
        disabled={charCount < 50 || charCount > 5000}
      >
        Analyze Resume
      </button>
    </div>
  );
};

export default JobDescriptionInput;
