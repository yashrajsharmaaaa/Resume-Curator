import { useState } from 'react';
// Icons removed for monochromatic design

const DashboardLayout = ({ children, currentStep = 'upload' }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Home', icon: Home, current: currentStep === 'dashboard' },
    { name: 'Schedule', icon: Calendar, current: false },
    { name: 'Courses', icon: BookOpen, current: false },
    { name: 'Videos', icon: Play, current: false },
    { name: 'Finalytics', icon: BarChart3, current: currentStep === 'upload' || currentStep === 'job' || currentStep === 'results' },
    { name: 'Settings', icon: Settings, current: false },
  ];

  const bottomNavigation = [
    { name: 'Support', icon: HelpCircle },
    { name: 'Log Out', icon: LogOut },
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAFAFA' }}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ backgroundColor: '#14121E' }}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-20 shrink-0 items-center px-8">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
                <div className="w-6 h-6 bg-black rounded-md"></div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-6 py-8">
            <div className="space-y-2">
              {navigation.map((item) => (
                <div
                  key={item.name}
                  className={`group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 cursor-pointer ${
                    item.current
                      ? 'bg-white bg-opacity-15 text-white'
                      : 'text-white text-opacity-70 hover:bg-white hover:bg-opacity-10 hover:text-white'
                  }`}
                >
                  <item.icon className="mr-4 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </div>
              ))}
            </div>
          </nav>

          {/* Bottom Navigation */}
          <div className="px-6 pb-8">
            <div className="space-y-2">
              {bottomNavigation.map((item) => (
                <div
                  key={item.name}
                  className="group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 cursor-pointer text-white text-opacity-70 hover:bg-white hover:bg-opacity-10 hover:text-white"
                >
                  <item.icon className="mr-4 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Top header */}
        <header className="bg-white border-b border-gray-100 sticky top-0 z-30">
          <div className="flex h-16 items-center justify-between px-8">
            <div className="flex items-center">
              <button
                type="button"
                className="lg:hidden -m-2.5 p-2.5"
                style={{ color: '#14121E' }}
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="h-6 w-6" />
              </button>
              
              <div className="ml-4 lg:ml-0">
                <h1 className="text-2xl font-semibold" style={{ color: '#14121E' }}>
                  Resume Curator
                </h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  className="search-input pl-10"
                  placeholder="Search"
                />
              </div>

              {/* Notifications */}
              <button className="relative p-2 rounded-xl hover:bg-gray-50 transition-colors">
                <Bell className="h-5 w-5" style={{ color: '#14121E' }} />
                <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
              </button>

              {/* Settings */}
              <button className="p-2 rounded-xl hover:bg-gray-50 transition-colors">
                <Settings className="h-5 w-5" style={{ color: '#14121E' }} />
              </button>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="px-8 pt-2 pb-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;

