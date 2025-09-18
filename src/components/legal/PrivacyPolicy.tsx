import { ScrollArea } from '../ui/scroll-area';

export default function PrivacyPolicy() {
  return (
    <ScrollArea className="h-[70vh] pr-4">
      <div className="space-y-6 text-sm">
        <div>
          <h1 className="text-2xl mb-4 aurum-text-gradient">Privacy Policy</h1>
          <p className="text-muted-foreground mb-4">
            <strong>Effective Date:</strong> September 2025
          </p>
          <p className="text-muted-foreground mb-6">
            Aurum Life operates a personal productivity platform. This Privacy Policy informs 
            you of our policies regarding the collection, use, and disclosure of personal data 
            when you use our Service and the choices you have associated with that data.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">1. Information We Collect</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-foreground mb-2">1.1 Personal Information</h3>
              <p className="text-muted-foreground mb-2">When you create an account, we collect:</p>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Name and email address</li>
                <li>Profile information you choose to provide</li>
                <li>Account preferences and settings</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium text-foreground mb-2">1.2 Content and Usage Data</h3>
              <p className="text-muted-foreground mb-2">To provide the Service, we collect and store:</p>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Your personal goals, projects, tasks, and notes</li>
                <li>Journal entries and reflections</li>
                <li>Files and attachments you upload</li>
                <li>Voice recordings (processed locally when possible)</li>
                <li>Usage patterns and interaction data with the Service</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">1.3 Technical Information</h3>
              <p className="text-muted-foreground mb-2">We automatically collect:</p>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>IP address and general location information</li>
                <li>Browser type and version</li>
                <li>Device information and operating system</li>
                <li>Log data including access times and pages viewed</li>
                <li>Cookies and similar tracking technologies</li>
              </ul>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">2. How We Use Your Information</h2>
          <div className="space-y-3">
            <div>
              <h3 className="font-medium text-foreground mb-2">2.1 Provide the Service</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Create and maintain your account</li>
                <li>Store and organize your personal data</li>
                <li>Enable core productivity features</li>
                <li>Provide AI-powered insights and recommendations</li>
                <li>Process voice-to-text functionality</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">2.2 Improve the Service</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Analyze usage patterns to enhance features</li>
                <li>Develop new functionality</li>
                <li>Fix bugs and optimize performance</li>
                <li>Conduct research and analytics</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">2.3 Communication</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Send important service notifications</li>
                <li>Respond to your inquiries and support requests</li>
                <li>Share product updates (with your consent)</li>
                <li>Send security alerts when necessary</li>
              </ul>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">3. Data Sharing and Disclosure</h2>
          <div className="space-y-3">
            <div>
              <h3 className="font-medium text-foreground mb-2">3.1 No Sale of Personal Data</h3>
              <p className="text-muted-foreground">
                We do not sell, trade, or rent your personal information to third parties.
              </p>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">3.2 Service Providers</h3>
              <p className="text-muted-foreground mb-2">
                We may share information with trusted third-party service providers who assist us:
              </p>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Cloud hosting and storage providers</li>
                <li>Analytics and monitoring services</li>
                <li>Customer support platforms</li>
                <li>Payment processors (for subscription plans)</li>
              </ul>
              <p className="text-muted-foreground mt-2">
                All service providers are bound by confidentiality agreements and are only 
                authorized to use your information as necessary to provide services to us.
              </p>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">4. Data Storage and Security</h2>
          <div className="space-y-3">
            <div>
              <h3 className="font-medium text-foreground mb-2">4.1 Data Security</h3>
              <p className="text-muted-foreground">
                We implement appropriate technical and organizational security measures to protect 
                your personal information against unauthorized access, alteration, disclosure, or destruction.
              </p>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">4.2 Encryption</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Data is encrypted in transit using industry-standard protocols</li>
                <li>Sensitive data is encrypted at rest</li>
                <li>Voice data is processed securely and locally when possible</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-foreground mb-2">4.3 Access Controls</h3>
              <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                <li>Strict access controls limit who can access your data</li>
                <li>Regular security audits and monitoring</li>
                <li>Employee training on data protection practices</li>
              </ul>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">5. Data Retention</h2>
          <p className="text-muted-foreground mb-3">
            We retain your personal information for as long as your account is active or as 
            needed to provide the Service.
          </p>
          <div className="space-y-2">
            <p className="text-muted-foreground">
              <strong>Deletion Timeline:</strong> Upon account deletion, personal data is removed 
              within 30 days. Backup systems may retain data for up to 90 days for disaster recovery.
            </p>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">6. Your Rights and Choices</h2>
          <div className="space-y-2">
            <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
              <li><strong>Data Access:</strong> Request access to the personal information we hold about you</li>
              <li><strong>Data Portability:</strong> Export your data at any time using our data export functionality</li>
              <li><strong>Data Correction:</strong> Correct inaccurate information through your account settings</li>
              <li><strong>Data Deletion:</strong> Delete your account and associated data at any time</li>
              <li><strong>Marketing Communications:</strong> Opt out of promotional communications</li>
            </ul>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">7. Cookies and Tracking</h2>
          <p className="text-muted-foreground mb-2">We use cookies and similar technologies for:</p>
          <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
            <li>Essential functionality (login, preferences)</li>
            <li>Analytics and performance monitoring</li>
            <li>Security and fraud prevention</li>
          </ul>
          <p className="text-muted-foreground mt-3">
            You can control cookies through your browser settings. You can also opt out of 
            analytics tracking in your account settings.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">8. Children's Privacy</h2>
          <p className="text-muted-foreground">
            Our Service is not intended for children under 13 years of age. We do not knowingly 
            collect personal information from children under 13. If we become aware that we have 
            collected personal data from a child under 13, we will take steps to delete such information.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">9. Changes to Privacy Policy</h2>
          <p className="text-muted-foreground mb-2">We may update our Privacy Policy from time to time. We will notify you of any changes by:</p>
          <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
            <li>Posting the new Privacy Policy on this page</li>
            <li>Sending an email notification for material changes</li>
            <li>Providing notice through the Service</li>
          </ul>
        </div>

        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            <strong>Last updated:</strong> September 2025
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            If you have any questions about this Privacy Policy or our privacy practices, 
            please contact us at privacy@aurumlife.com
          </p>
        </div>
      </div>
    </ScrollArea>
  );
}