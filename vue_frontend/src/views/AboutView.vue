<template>
  <div class="container mx-auto px-4 md:py-8 max-w-4xl">
    <h1 class="text-4xl font-bold mb-6">About AiAWE</h1>

    <div class="space-y-6 text-lg">
      <section>
        <h2 class="text-2xl font-semibold mb-3">Our Mission</h2>
        <p>
          AiAWE (AI - Automated Writing Evaluation) is a research project at Waseda University
          that aims to ...
        </p>
      </section>

      <section>
        <h2 class="text-2xl font-semibold mb-3">Research Team</h2>
        <div class="space-y-4">
          <div>
            <h3 class="text-xl font-medium">John M. Gayed</h3>
            <p class="text-muted-foreground">Principal Investigator</p>
            <p>Received his Ph.D from the Tokyo Institute of Technology researching AI writing aids and their impact on L2 learners. 
              He is currently an Associate Professor and Program Coordinator at the Global Education Center, Waseda University. 
              His research in CALL primarily focuses on L2 writing assessment, in addition to researching how digital aids impact cognitive load and writing fluency.
              <a href="https://scholar.google.com/citations?user=0wxpbbYAAAAJ&hl=en&oi=ao" class="text-primary hover:underline">John’s Google Scholar page</a></p>
          </div>
          <div>
            <h3 class="text-xl font-medium">Judy Wang</h3>
            <p class="text-muted-foreground">Co-Investigator</p>
            <p>Research interests include second language acquisition (SLA), natural language processing (NLP), and artificial intelligence (AI), focusing on the evolving role of digital technology in language education.
              Recently, Judy's, work has focused on Computer-Assisted Language Learning (CALL), covering areas like Game-Based Language Learning (GBLL), 
              corpus studies, automated essay evaluation, and computer-based testing.
              <a href="https://scholar.google.com/citations?user=Ftb5Q3EAAAAJ" class="text-primary hover:underline">Judy’s Google Scholar page</a></p>
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-2xl font-semibold mb-3">The Project</h2>
        <p>
          AiAWE is a research project that aims to apply Large Language Models (LLMs) to Automated Writing Evaluation (AWE). While there will always be a place for human assessment in student learning, LLMs, unlike human graders, 
          can evaluate a high volume of essays while maintaining consistency across assessments. With our research we found that LLMs can provide reliable and scalable quantitative evaluation, in addition to qualitative feedback to writers.
          In our research, we finetune and adjust LLM parameters to produce highly accurate and reliable assessment compared to gold-standard ETS professional essay graders. <br>
          The finetuning dataset used in this research is based on the TOEFL iBT Public Use Dataset provided to us via grant application to ETS. More information about the dataset can be found in our publication: 
          <br>Wang, Q., & Gayed, J. M. (2024). Effectiveness of large language models in automated evaluation of argumentative essays: finetuning vs. zero-shot prompting. Computer Assisted Language Learning, 1–29. 
          <a href="https://doi.org/10.1080/09588221.2024.2371395" class="text-primary hover:underline">LINK TO ARTICLE</a><br>
          This dataset was chosen because TOEFL is an internationally acknowledged test, and the Independent Writing Task is a typical example of argumentative writing that L2 students often encounter.
          All of the models used in AiAWE are finetuned on the TOEFL iBT Public Use Dataset.<br><br>
          AiAWE can be used individually for student practice, giving them low-risk formative assessment as they practice writing.
          In addition, educators can also use AiAWE in more formal summative assessment in their classrooms. 
          <br><br>AiAWE works best assessing argumentative writing that is around 1,000 words. <br> AiAWE can also be used by teachers with special features such as bulk grading, class creation, and bulk user creation. 
          <br>If you are interesting in receiving such access, please contact admin@aiawe.app <br>
          Currently AiAWE support three LLMs:<br>
        <ul class="list-disc list-inside mt-2 space-y-2">
          <li>Llama 3.3 70B is an open access LLM that is being hosted on the researcher’s server. Since it is a locally hosted LLM, student submissions are not sent to a third party via API, but instead are processed locally. 
            Depending on how many users are using the system, it may take some time to return a result. As the local LLM doesn't cost us any API fees, the usage quota per user is set very high. The model achieves a 
            Quadratic Weighted Kappa (QWK) of 0.77 against ground truth scores from ETS, rivaling ETS’s own internal e-rater engine.</li>
          <li>GPT 3.5 Turbo. The submission will be sent to OpenAI’s servers for assessment. This was our first attempt at finetuning an advanced LLM for AWE. This is the model that was used in the above mentioned Wang, Q., & Gayed, J. M. (2024) paper. 
            The model achieves a QWK of 0.78 and a Root Mean Square Error (RMSE) of 0.57 against ground truth scores from ETS, rivaling ETS’s e-rater engine.</li>
          <li>GPT 4o. The submission will be sent to OpenAI’s servers for assessment. The more advanced model achieves even better results with a QWK nearing 0.9 against ground truth scores from ETS, a substantial improvement over ETS’s own system.</li>
        </ul>
        </p>
      </section>

      <section>
        <h2 class="text-2xl font-semibold mb-3">Funding, Citation</h2>
        <ul class="list-disc list-inside mt-2 space-y-2">
          <li>If you would like to cite AiAWE in your research, please use the following citation: Gayed, J. M., Wang, Q. (2025). AI-AWE (Version 1.0) [Web application]. https://app.awade.gec.waseda.ac.jp </li>
          <li>AiAWE is funded by the Japan Society for the Promotion of Science (JSPS) via the Grants-in-Aid for Scientific Research (KAKENHI) Grant Number 22K00718 and the Telecommunications Advancement Foundation in Japan.</li>
        </ul>
      </section>

      <section id="rubric">
        <h2 class="text-2xl font-semibold mb-3">ETS Rubric Used by AiAWE</h2>
    <div class="mt-8 max-w-3xl mx-auto">
      <img
        src="@/assets/imgs/toeflrubric.png"
        alt="ETS TOEFL RUBRIC"
        class="w-full hover:opacity-90 transition-opacity"
      />
    </div>
      </section>
      
      <section>
        <h2 class="text-2xl font-semibold mb-3">Contact</h2>
        <p>
          For research collaboration or general inquiries, please contact us at:
          <a href="mailto:admin@aiawe.app" class="text-primary hover:underline">admin@aiawe.app</a>
        </p>
      </section>
    </div>
  </div>
</template>
