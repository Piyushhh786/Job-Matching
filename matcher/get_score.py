from sklearn.metrics.pairwise import cosine_similarity
from model.net import load_imp_sentence_classifier,vectorizer
from normalizer.preprocess_data import is_noise
import numpy as np
import json
import torch
import re
from notifier.telegram import notify_telegram
from normalizer.preprocess_data import extract_sentences_from_html,process_sentence,is_noise
profile_path = r"E:\Desktop\webAutomation\utlis\profile.json" # org profile
model = load_imp_sentence_classifier("imp_sentence_classifier.pth",0.01)
model.eval()

with open(profile_path,'r',encoding='utf-8') as f:
    data = json.load(f)

def get_project_with_score(job_description, top_k=2):
    sentences = extract_sentences_from_html(job_description)

    important_sentences = []
    min_required_experience = None

    # -------- STEP 1: JD ANALYSIS --------
    for s in sentences:
        # ---- experience extraction ----
        if "experience" in s.lower() and re.search(r"\d+\+ ", s):
            nums = [int(x) for x in re.findall(r"\d+", s)]
            if nums:
                years = min(nums)
                min_required_experience = (
                    years if min_required_experience is None
                    else min(min_required_experience, years)
                )

        # ---- importance classification ----
        clean_s = process_sentence(s)
        if not clean_s or is_noise(s):
            continue

        x = vectorizer.transform([clean_s]).toarray()
        x = torch.from_numpy(x).float()

        with torch.no_grad():
            pred = torch.argmax(model(x), dim=1).item()

        if pred == 1 :
            if not is_noise(s):
                important_sentences.append(s)

    if not important_sentences:
        return {"error": "No important JD sentences detected"}

    jd_vectors = vectorizer.transform(important_sentences)

    # -------- STEP 2: PROJECT SCORING --------
    project_scores = []
    total_bullets = 0

    for project in data["projects"]:
        clean_bullets = [process_sentence(b) for b in project["bullets"]]
        clean_bullets = [b for b in clean_bullets if b]

        if project.get("skills"):
            clean_bullets.append(" ".join(project["skills"]))

        total_bullets += len(clean_bullets)
        if not clean_bullets:
            continue

        proj_vectors = vectorizer.transform(clean_bullets)
        sims = cosine_similarity(proj_vectors, jd_vectors)

        score = float(np.mean(np.max(sims, axis=1)))

        project_scores.append({
            "name": project["name"],
            "domain": project["domain"],
            "level": project["level"],
            "score": round(score * 100, 2),
            "live": project.get("live"),
            "github": project.get("github"),
            "skills": project.get("skills"),
            "state":project.get('state'),
            "bullets": project.get("bullets")
        })

    # -------- STEP 3: TOP-K PROJECTS --------
    project_scores.sort(key=lambda x: x["score"], reverse=True)
    top_projects = project_scores[:top_k]


    # -------- STEP 4: ATS SCORE --------
    max_possible = min(len(important_sentences),top_k*4)
    achieved = sum(p["score"] for p in top_projects) / top_k
    ats_score = round((achieved / max_possible) * 100, 2) if max_possible else 0

    # -------- FINAL JSON --------
    return {
        "min_required_experience": min_required_experience,
        "important_jd_sentences": len(important_sentences),
        "top_projects": top_projects,
        "ats_score": ats_score,
        "important_sentences": important_sentences
    }

# jd ="<p style=\"text-align:left\"><b><i><span>Welcome to Warner Bros. Discovery… the stuff dreams are made of.</span></i></b></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><b><span>Who We Are… </span></b></p><p style=\"text-align:left\"><span>When we say, “the stuff dreams are made of,” we’re not just referring to the world of wizards, dragons and superheroes, or even to the wonders of Planet Earth. Behind WBD’s vast portfolio of iconic content and beloved brands, are the <i>storytellers</i> bringing our characters to life, the<i> creators</i> bringing them to your living rooms and the <i>dreamers</i> creating what’s next…</span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span>From brilliant creatives, to technology trailblazers, across the globe, WBD offers career defining opportunities, thoughtfully curated benefits, and the tools to explore and grow into your best selves. Here you are supported, here you are celebrated, here you can thrive.</span></p><p style=\"text-align:inherit\"></p><p><b>Sr Software Engineer, Consumer </b>- <b>Hyderabad, India.</b></p><p></p><p><b>About Warner Bros. Discovery: </b>Warner Bros. Discovery, a premier global media and entertainment company, offers audiences the world&#39;s most differentiated and complete portfolio of content, brands and franchises across television, film, streaming and gaming. The new company combines Warner Media’s premium entertainment, sports and news assets with Discovery&#39;s leading non-fiction and international entertainment and sports businesses. For more information, please visit www.wbd.com.</p><p></p><p><b>Meet Our Team: </b>The Trust and Safety team is responsible for providing a rich portfolio of privacy, fraud and abuse prevention solutions to end customers wherever they are located across the globe. These global solutions range from privacy compliance services for consent management, individual rights request management to client and server-side fraud and abuse detection and prevention tools.</p><p>The Trust and Safety team is responsible for integrating these services and tools into a global, multi-tenant, direct to consumer product platform. The Trust and Safety solutions are business-critical, top-tier services that cannot afford any downtime and must be highly scalable with prime-time events with millions of viewers. We are setting up an India Development Center to better support our global streaming services and assist international teams. We are looking for a Senior Engineer to join the Trust and Safety team and enable the global expansion of our services.</p><p></p><p><b>Roles &amp; Responsibilities:</b></p><p>• Build high-performance, stable, and scalable systems deployed in production. • Always champion engineering and operational excellence.</p><p>• Drive best practices and set standards within the team.</p><p>• Understand a broad range of data structures, algorithms design, and know how, when and when not to use them.</p><p>• Exercise good judgment when balancing immediate and long-term business needs.</p><p>• Creatively think and innovate to deliver delightful experiences for customers.</p><p>• Always demonstrate data-driven decision-making and continuously seek solutions to challenging problems.</p><p>• Hold strong opinions while remaining open to other perspectives.</p><p>• Consistently deliver results, with quality, in a fast-paced environment.</p><p>• Collaborate with peers, share knowledge, and contribute to technical decisions. • Lead major functional changes in existing or new software systems.</p><p>• Investigate production issues, identify root causes, and improve processes</p><p>. • Document code, designs, and processes for clarity.</p><p>• Provide guidance on design, coding, and operational best practices. • Establish best practices and quality standards within the team. • Mentor junior engineers and positively influence the team.</p><p></p><p><b>What to Bring:</b> • Bachelor’s degree with 5 – 8 years of experience as a software developer. • Proficient in Java (Vert.x or Spring Boot framework is a plus) or other JVM languages.</p><p>• Proficient in JavaScript frameworks like React or Angular, HTML/CSS, and UI/UX design principles.</p><p>• Experience with persistence and caching solutions such as PostgreSQL, Redis, Elasticsearch.</p><p>• Experience in building and operating global-scale large platform services in non-prod and prod environments.</p><p>• Ability to collaborate effectively with remote peers across disparate geographies and time zones.</p><p>• Strong CS fundamentals; strong technical understanding of Kubernetes-based microservice architectures, caching solutions, messaging services, DB services, API gateways, service mesh, and infrastructure-as-code technologies/processes.</p><p>• Direct experience with at least one cloud provider (AWS, GCP, Azure, or other). • Experience establishing and improving data-driven infrastructure and service KPIs such as performance, scale, availability, reliability, security.</p><p>• A strong understanding of security best practices and a high bar for protecting customer data.</p><p>• Ability to implement alerting, metrics, and logging using tools like Prometheus, CloudWatch, Kibana, PagerDuty.</p><p>• Familiar with asynchronous, non-blocking, functional/reactive styles of programming. Hands-on experience with frameworks such as Spring WebFlux, Vert.x, Node.js.</p><p>• Operational Experience to run services globally; on-call rotation, incident response, playbooks.</p><p>• Excellent written and verbal communication skills with emphasis on technical documentation.</p><p><b>What We Offer:</b> ● A Great Place to work. ● Equal opportunity employer ● Fast track growth opportunitie</p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p><b><span>How We Get Things Done…</span></b></p><p></p><p><span>This last bit is probably the most important! Here at WBD, our guiding principles are the core values by which we operate and are central to how we get things done. You can find them at </span><a href=\"http://www.wbd.com/guiding-principles/\" target=\"_blank\"><span><span><span><span><span><span><span><span><span><span><span><span><span><span><span><span><span>www.wbd.com/guiding-principles/</span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></span></a><span> along with some insights from the team on what they mean and how they show up in their day to day. We hope they resonate with you and look forward to discussing them during your interview.</span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><b><span>Championing Inclusion at WBD</span></b></p>Warner Bros. Discovery embraces the opportunity to build a workforce that reflects a wide array of perspectives, backgrounds and experiences. Being an equal opportunity employer means that we take seriously our responsibility to consider qualified candidates on the basis of merit, regardless of sex, gender identity, ethnicity, age, sexual orientation, religion or belief, marital status, pregnancy, parenthood, disability or any other category protected by law.<p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span>If you’re a qualified candidate with a disability and you require adjustments or accommodations during the job application and/or recruitment process, please visit our </span><a href=\"https://careers.wbd.com/global/en/accessibility\" target=\"_blank\">accessibility page</a><span> for instructions to submit your request.</span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p>"
# res = get_project_with_score(jd)
# print(res['top_projects'])
# print(f"Imp sentence\n {res['important_sentences']}")
# print(res['ats_score'])
# if(res['ats_score']>84):
#     notify_telegram(top_projects=res['top_projects'],job_url="xyz")
# profile_path = r"E:\Desktop\webAutomation\resume_generator\profile.json"
# with open(profile_path,'r',encoding='utf-8') as f:
#     base_profile = json.load(f)
#     base_profile['projects'] = res['top_projects']
#     print(f"The Updated the json file ------------------\n")
# for proj in base_profile['projects']:
#     print(proj['bullets'])

# print(res['ats_score'])
# print(res['min_required_experience'])
# for x in res["top_projects"]:
#     print(x)
# print(res['important_sentences'])

# for x,s in imp_sent:
#     print(f"{s}\n")
# print("-----------------")
# for x in total:
#     print(x,len(imp_sent))

