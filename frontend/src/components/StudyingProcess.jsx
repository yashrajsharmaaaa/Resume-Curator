const StudyingProcess = () => {
  const chartData = [
    { day: '16 Aug', value: 80, isActive: true },
    { day: '17 Aug', value: 60, isActive: true },
    { day: '18 Aug', value: 40, isActive: false },
    { day: '19 Aug', value: 90, isActive: true },
    { day: '20 Aug', value: 45, isActive: false },
    { day: '21 Aug', value: 85, isActive: true },
    { day: '22 Aug', value: 95, isActive: true },
  ];

  const maxValue = Math.max(...chartData.map(d => d.value));

  return (
    <div className="container">
      <div className="mb-lg">
        <h3 className="text-xl text-gray-800 mb-md">
          Studying Process
        </h3>
        <div className="space-y-sm">
          <button className="text-sm text-gray-800 font-semibold minimal-border p-sm">
            Time
          </button>
          <button className="text-sm text-gray-500 p-sm hover-opacity">Activity</button>
          <button className="text-sm text-gray-500 p-sm hover-opacity">Balance</button>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-lg">
        <div className="space-y-sm text-xs text-gray-500 mb-md">
          <div>10h</div>
          <div>8h</div>
          <div>6h</div>
          <div>4h</div>
          <div>2h</div>
          <div>0h</div>
        </div>
        
        <div className="space-y-md">
          {chartData.map((item, index) => (
            <div key={index} className="space-y-xs">
              <div className="text-xs text-gray-500">
                {item.day}
              </div>
              <div className="minimal-border p-sm">
                <div 
                  className={`h-4 ${item.isActive ? 'bg-gray-800' : 'bg-gray-200'}`}
                  style={{ width: `${(item.value / maxValue) * 100}%` }}
                />
                <div className="text-xs text-gray-700 mt-xs">
                  {item.value}% ({Math.round(item.value / 10)}h)
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-md">
        <div className="space-y-sm">
          <div className="text-sm font-semibold text-gray-800">
            21 Active Subjects
          </div>
          <div className="text-sm font-semibold text-gray-800">
            78% Completion Rate
          </div>
        </div>
        
        <div className="text-sm text-gray-500">
          Last week
        </div>
      </div>
    </div>
  );
};

export default StudyingProcess;