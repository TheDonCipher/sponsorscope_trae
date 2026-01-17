import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Info, Clock, Shield, Eye, FileText } from 'lucide-react';

interface ComplianceTest {
  test_id: string;
  scenario: string;
  platform: string;
  handle: string;
  expected_warning: string;
  expected_epistemic: string;
  passed: boolean;
  failures: string[];
  warnings: string[];
}

interface ComplianceReport {
  report_metadata: {
    generated_at: string;
    test_framework_version: string;
    total_tests: number;
    passed_tests: number;
    failed_tests: number;
    success_rate: string;
  };
  compliance_summary: {
    watermark_persistence: boolean;
    warning_display: boolean;
    metadata_standards: boolean;
    probabilistic_framing: boolean;
  };
  failure_analysis: {
    metadata: string[];
    watermark: string[];
    warning: string[];
    framing: string[];
  };
  detailed_results: ComplianceTest[];
  recommendations: string[];
}

const UXComplianceDashboard: React.FC = () => {
  const [complianceData, setComplianceData] = useState<ComplianceReport | null>(null);
  const [selectedTest, setSelectedTest] = useState<ComplianceTest | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load compliance report data
    fetch('/docs/audits/ux_compliance_report.json')
      .then(response => response.json())
      .then(data => {
        setComplianceData(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Failed to load compliance report:', error);
        setIsLoading(false);
      });
  }, []);

  const getStatusIcon = (passed: boolean) => {
    return passed ? 
      <CheckCircle className="w-5 h-5 text-green-500" /> : 
      <XCircle className="w-5 h-5 text-red-500" />;
  };

  const getComplianceIcon = (status: boolean) => {
    return status ? 
      <CheckCircle className="w-6 h-6 text-green-500" /> : 
      <AlertTriangle className="w-6 h-6 text-yellow-500" />;
  };

  const getWarningTypeColor = (warningType: string) => {
    const colors = {
      'blocked': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'sparse': 'bg-blue-100 text-blue-800 border-blue-300',
      'rate_limit': 'bg-purple-100 text-purple-800 border-purple-300',
      'private': 'bg-gray-100 text-gray-800 border-gray-300',
      'system': 'bg-indigo-100 text-indigo-800 border-indigo-300'
    };
    return colors[warningType as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getEpistemicStateColor = (epistemic: string) => {
    const colors = {
      'robust': 'bg-green-100 text-green-800 border-green-300',
      'limited': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'insufficient': 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[epistemic as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Clock className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-semibold text-gray-700">Loading Compliance Report...</h2>
        </div>
      </div>
    );
  }

  if (!complianceData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Failed to Load Report</h2>
          <p className="text-gray-500 mt-2">Unable to load UX compliance data</p>
        </div>
      </div>
    );
  }

  const { report_metadata, compliance_summary, failure_analysis, detailed_results, recommendations } = complianceData;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">UX Compliance Dashboard</h1>
              <p className="text-gray-600">SponsorScope.ai Screenshot Audit Validation</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-gray-900">{report_metadata.success_rate}</div>
              <div className="text-sm text-gray-500">Success Rate</div>
            </div>
          </div>
          
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>Generated: {new Date(report_metadata.generated_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4" />
              <span>Framework v{report_metadata.test_framework_version}</span>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{report_metadata.total_tests}</div>
                <div className="text-sm text-gray-500">Total Tests</div>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-600">{report_metadata.passed_tests}</div>
                <div className="text-sm text-gray-500">Passed</div>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-red-600">{report_metadata.failed_tests}</div>
                <div className="text-sm text-gray-500">Failed</div>
              </div>
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{compliance_summary.watermark_persistence ? '100%' : '0%'}</div>
                <div className="text-sm text-gray-500">Watermark OK</div>
              </div>
              <Shield className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Compliance Summary */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Compliance Areas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getComplianceIcon(compliance_summary.watermark_persistence)}
                <div>
                  <div className="font-medium text-gray-900">Watermark Persistence</div>
                  <div className="text-sm text-gray-500">Anti-tampering watermarks</div>
                </div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                compliance_summary.watermark_persistence 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {compliance_summary.watermark_persistence ? 'PASS' : 'FAIL'}
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getComplianceIcon(compliance_summary.warning_display)}
                <div>
                  <div className="font-medium text-gray-900">Warning Display</div>
                  <div className="text-sm text-gray-500">Appropriate warning banners</div>
                </div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                compliance_summary.warning_display 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {compliance_summary.warning_display ? 'PASS' : 'FAIL'}
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getComplianceIcon(compliance_summary.metadata_standards)}
                <div>
                  <div className="font-medium text-gray-900">Metadata Standards</div>
                  <div className="text-sm text-gray-500">Naming conventions</div>
                </div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                compliance_summary.metadata_standards 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {compliance_summary.metadata_standards ? 'PASS' : 'FAIL'}
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                {getComplianceIcon(compliance_summary.probabilistic_framing)}
                <div>
                  <div className="font-medium text-gray-900">Probabilistic Framing</div>
                  <div className="text-sm text-gray-500">Uncertainty language</div>
                </div>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                compliance_summary.probabilistic_framing 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {compliance_summary.probabilistic_framing ? 'PASS' : 'FAIL'}
              </span>
            </div>
          </div>
        </div>

        {/* Test Results */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Test List */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Results</h2>
            <div className="space-y-3">
              {detailed_results.map((test) => (
                <div 
                  key={test.test_id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedTest?.test_id === test.test_id 
                      ? 'bg-blue-50 border-blue-200' 
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                  onClick={() => setSelectedTest(test)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(test.passed)}
                      <div>
                        <div className="font-medium text-gray-900 text-sm">{test.test_id}</div>
                        <div className="text-xs text-gray-500">{test.platform} • {test.handle}</div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getWarningTypeColor(test.expected_warning)}`}>
                        {test.expected_warning}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getEpistemicStateColor(test.expected_epistemic)}`}>
                        {test.expected_epistemic}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Test Details */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Details</h2>
            {selectedTest ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">{selectedTest.test_id}</h3>
                  <p className="text-sm text-gray-600 mb-4">{selectedTest.scenario}</p>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-gray-500">Platform</div>
                      <div className="font-medium">{selectedTest.platform}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Handle</div>
                      <div className="font-medium">{selectedTest.handle}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Expected Warning</div>
                      <div className="font-medium">{selectedTest.expected_warning}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Epistemic State</div>
                      <div className="font-medium">{selectedTest.expected_epistemic}</div>
                    </div>
                  </div>
                </div>

                {/* Failures */}
                {selectedTest.failures.length > 0 && (
                  <div>
                    <h4 className="font-medium text-red-700 mb-2 flex items-center gap-2">
                      <XCircle className="w-4 h-4" />
                      Failures ({selectedTest.failures.length})
                    </h4>
                    <div className="space-y-1">
                      {selectedTest.failures.map((failure, index) => (
                        <div key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                          {failure}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {selectedTest.warnings.length > 0 && (
                  <div>
                    <h4 className="font-medium text-yellow-700 mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      Warnings ({selectedTest.warnings.length})
                    </h4>
                    <div className="space-y-1">
                      {selectedTest.warnings.map((warning, index) => (
                        <div key={index} className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
                          {warning}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pass Status */}
                {selectedTest.passed && selectedTest.failures.length === 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="font-medium text-green-800">All validations passed</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Select a test to view details</p>
              </div>
            )}
          </div>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
            <div className="space-y-3">
              {recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <Info className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-blue-800">{recommendation}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Failure Analysis */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mt-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Failure Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Watermark Issues ({failure_analysis.watermark.length})</h3>
              <div className="space-y-1">
                {failure_analysis.watermark.slice(0, 3).map((failure, index) => (
                  <div key={index} className="text-sm text-gray-600 bg-red-50 p-2 rounded">
                    {failure}
                  </div>
                ))}
                {failure_analysis.watermark.length > 3 && (
                  <div className="text-sm text-gray-500">+{failure_analysis.watermark.length - 3} more</div>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Framing Issues ({failure_analysis.framing.length})</h3>
              <div className="space-y-1">
                {failure_analysis.framing.slice(0, 3).map((failure, index) => (
                  <div key={index} className="text-sm text-gray-600 bg-yellow-50 p-2 rounded">
                    {failure}
                  </div>
                ))}
                {failure_analysis.framing.length > 3 && (
                  <div className="text-sm text-gray-500">+{failure_analysis.framing.length - 3} more</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UXComplianceDashboard;