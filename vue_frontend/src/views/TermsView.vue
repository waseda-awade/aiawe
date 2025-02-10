<template>
  <div class="max-w-4xl mx-auto px-4 md:py-8">
    <h1 class="text-4xl font-bold mb-4">
      Terms of Service and Privacy Policy
    </h1>
    <p class="text-muted-foreground text-sm mb-6">Last updated: 2/10/2025</p>

    <div class="prose dark:prose-invert max-w-none">
      <div class="bg-muted/50 rounded-lg p-4 mb-8 text-muted-foreground">
        <p class="!mt-0">By accessing or using the AiAWE application ("App"), you agree to the following Terms of
          Service and Privacy Policy.</p>
      </div>

      <div class="space-y-8">
        <section>
          <h2>1. Use of the App</h2>
          <ul>
            <li>The App is provided for non-commercial, educational, and research purposes.</li>
            <li>Users under 18 should have parental or guardian consent to use the App.</li>
            <li>Users are responsible for the accuracy and legality of the information they submit.</li>
          </ul>
        </section>

        <section>
          <h2>2. User Submissions</h2>
          <ul>
            <li>User submissions, including but not limited to text and other content, are private and will not be
              shared publicly within the App.</li>
            <li>AiAWE may use user submissions to improve the quality of the App.</li>
            <li>Users retain ownership of their submissions but grant AiAWE a non-exclusive right to use them for
              research and development purposes.</li>
          </ul>
        </section>

        <section>
          <h2>3. Privacy and Data Storage</h2>
          <ul>
            <li>User data, including names, email addresses, and submissions, is stored at the researcher's host
              university.</li>
            <li>Users can request to delete all their data by contacting <a
                href="mailto:admin@aiawe.app">admin@aiawe.app</a></li>
            <li>AiAWE does not sell or distribute personal data to third parties.</li>
          </ul>
        </section>

        <section>
          <h2>4. Use of OpenAI Models</h2>
          <ul>
            <li>The App provides access to OpenAI models, such as GPT-3.5 and GPT-4o.</li>
            <li>Users who engage with these models must follow OpenAI's privacy policy, which can be reviewed at:
              <a href="https://openai.com/enterprise-privacy" target="_blank" rel="noopener noreferrer"
                class="inline-flex items-center">
                OpenAI Enterprise Privacy
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </li>
            <li>AiAWE does not control the data processing performed by OpenAI and encourages users to review their
              privacy policies for further details.</li>
          </ul>
        </section>

        <section>
          <h2>5. External Services</h2>
          <ul>
            <li>Some features of the App require external API access.</li>
            <li>AiAWE is not responsible for any third-party services used within the App.</li>
          </ul>
        </section>

        <section>
          <h2>6. Security</h2>
          <ul>
            <li>We use industry-standard security measures, including encryption, to protect user data.</li>
            <li>Data transmitted between users and the App is encrypted using SSL/TLS protocols.</li>
            <li>Stored data is protected using encryption methods to minimize unauthorized access.</li>
            <li>Despite these measures, no method of transmission over the internet or electronic storage is
              completely secure.</li>
          </ul>
        </section>

        <section>
          <h2>7. Limitation of Liability</h2>
          <ul>
            <li>The App is provided "as is" without any warranties.</li>
            <li>AiAWE is not liable for any direct or indirect damages resulting from the use of the App.</li>
            <li>Users assume all risks associated with the use of the App.</li>
          </ul>
        </section>

        <section>
          <h2>8. Termination</h2>
          <ul>
            <li>AiAWE reserves the right to suspend or terminate user access at its discretion, particularly in cases
              of misuse or violation of these Terms.</li>
            <li>Users may discontinue use of the App at any time.</li>
          </ul>
        </section>

        <section>
          <h2>9. Changes to This Agreement</h2>
          <ul>
            <li>AiAWE may update these Terms and Privacy Policy from time to time.</li>
            <li>Continued use of the App constitutes acceptance of any modified terms.</li>
          </ul>
        </section>

        <section>
          <h2>10. Contact</h2>
          <ul>
            <li>For any questions regarding these Terms and Privacy Policy, contact us at
              <a href="mailto:admin@aiawe.app">
                admin@aiawe.app
              </a>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prose {
  @apply text-foreground;
}

.prose a {
  @apply text-primary hover:underline transition-colors;
}

.prose ul {
  @apply my-0;
}

.prose li {
  @apply my-0;
}

section h2 {
  @apply text-2xl font-semibold text-primary mb-4;
}

section ul {
  @apply list-disc pl-6 space-y-2;
}

section li {
  @apply my-0;
}

section a {
  @apply text-primary underline transition-colors;
}
</style>
