import { ScrollArea } from '../ui/scroll-area';

export default function TermsOfService() {
  return (
    <ScrollArea className="h-[70vh] pr-4">
      <div className="space-y-6 text-sm">
        <div>
          <h1 className="text-2xl mb-4 aurum-text-gradient">Terms of Service</h1>
          <p className="text-muted-foreground mb-4">
            <strong>Effective Date:</strong> September 2025
          </p>
          <p className="text-muted-foreground mb-6">
            Welcome to Aurum Life. These Terms of Service govern your use of the Aurum Life 
            personal operating system and productivity platform. By accessing or using our 
            Service, you agree to be bound by these Terms.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">1. Description of Service</h2>
          <p className="text-muted-foreground mb-4">
            Aurum Life is a personal productivity and life management platform that helps users 
            organize their goals, projects, tasks, and daily activities through a structured 
            hierarchy system. The Service includes features such as:
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
            <li>Personal goal and project management</li>
            <li>Task organization and tracking</li>
            <li>Journal and reflection tools</li>
            <li>AI-powered insights and recommendations</li>
            <li>Calendar integration and time blocking</li>
            <li>File storage and attachment capabilities</li>
            <li>Voice-to-text functionality</li>
            <li>Analytics and progress tracking</li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">2. User Accounts</h2>
          <div className="space-y-3">
            <div>
              <h3 className="font-medium text-foreground mb-2">2.1 Account Creation</h3>
              <p className="text-muted-foreground">
                To use certain features of the Service, you must register for an account. 
                When you create an account, you must provide information that is accurate, 
                complete, and current at all times.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-foreground mb-2">2.2 Account Security</h3>
              <p className="text-muted-foreground">
                You are responsible for safeguarding the password and all activities that 
                occur under your account. You must notify us immediately of any unauthorized 
                use of your account.
              </p>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">3. User Content and Data</h2>
          <div className="space-y-3">
            <div>
              <h3 className="font-medium text-foreground mb-2">3.1 Your Content</h3>
              <p className="text-muted-foreground">
                You retain full ownership of all content you submit, post, or display on or 
                through the Service. By submitting Your Content, you grant us a non-exclusive, 
                worldwide, royalty-free license to use, copy, reproduce, process, adapt, modify, 
                publish, transmit, display, and distribute Your Content solely for the purpose 
                of providing the Service.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-foreground mb-2">3.2 Data Export</h3>
              <p className="text-muted-foreground">
                You may export Your Content at any time through the Service's export functionality. 
                Upon account termination, you will have 30 days to export Your Content before it 
                may be deleted.
              </p>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">4. Prohibited Uses</h2>
          <p className="text-muted-foreground mb-3">You may not use the Service:</p>
          <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
            <li>For any unlawful purpose or to solicit others to perform unlawful acts</li>
            <li>To violate any international, federal, provincial, or state regulations, rules, laws, or local ordinances</li>
            <li>To infringe upon or violate our intellectual property rights or the intellectual property rights of others</li>
            <li>To harass, abuse, insult, harm, defame, slander, disparage, intimidate, or discriminate</li>
            <li>To submit false or misleading information</li>
            <li>To upload or transmit viruses or any other type of malicious code</li>
            <li>For any obscene or immoral purpose</li>
            <li>To interfere with or circumvent the security features of the Service</li>
          </ul>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">5. Service Availability</h2>
          <p className="text-muted-foreground">
            We strive to maintain high availability of the Service but do not guarantee 
            uninterrupted access. The Service may be temporarily unavailable due to 
            maintenance, updates, or unforeseen circumstances. We reserve the right to 
            withdraw or amend our Service at any time without notice.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">6. Privacy Policy</h2>
          <p className="text-muted-foreground">
            Your privacy is important to us. Please review our Privacy Policy, which also 
            governs your use of the Service, to understand our practices.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">7. Disclaimer of Warranties</h2>
          <p className="text-muted-foreground">
            The information on this Service is provided on an "as is" basis. To the fullest 
            extent permitted by law, we exclude all representations, warranties, and conditions 
            relating to our Service and the use of this Service.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">8. Limitation of Liability</h2>
          <p className="text-muted-foreground">
            In no case shall Aurum Life, its directors, officers, employees, affiliates, agents, 
            contractors, interns, suppliers, service providers, or licensors be liable for any 
            injury, loss, claim, or any direct, indirect, incidental, punitive, special, or 
            consequential damages of any kind.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">9. Termination</h2>
          <p className="text-muted-foreground">
            We may terminate or suspend your account and bar access to the Service immediately, 
            without prior notice or liability, under our sole discretion, for any reason 
            whatsoever and without limitation.
          </p>
        </div>

        <div>
          <h2 className="text-lg mb-3 text-primary">10. Changes to Terms</h2>
          <p className="text-muted-foreground">
            We reserve the right, at our sole discretion, to modify or replace these Terms at 
            any time. If a revision is material, we will try to provide at least 30 days notice 
            prior to any new terms taking effect.
          </p>
        </div>

        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            <strong>Last updated:</strong> September 2025
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            If you have any questions about these Terms of Service, please contact us at 
            support@aurumlife.com
          </p>
        </div>
      </div>
    </ScrollArea>
  );
}