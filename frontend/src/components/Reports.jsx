import React from 'react';

const Reports = () => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports</h1>
        <p className="text-gray-600">Generate and view comprehensive reports</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h3 className="text-lg font-semibold mb-4">Project Reports</h3>
          <p className="text-gray-600 mb-4">Generate detailed project performance reports</p>
          <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            Generate Report
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h3 className="text-lg font-semibold mb-4">Client Reports</h3>
          <p className="text-gray-600 mb-4">View client activity and engagement reports</p>
          <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            Generate Report
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <h3 className="text-lg font-semibold mb-4">Financial Reports</h3>
          <p className="text-gray-600 mb-4">Generate financial and budget reports</p>
          <button className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
            Generate Report
          </button>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md border">
        <h3 className="text-lg font-semibold mb-4">Recent Reports</h3>
        <div className="text-gray-600">
          <p>No reports generated yet. Click the buttons above to generate your first report.</p>
        </div>
      </div>
    </div>
  );
};

export default Reports;
