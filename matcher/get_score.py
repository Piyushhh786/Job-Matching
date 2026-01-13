from sklearn.metrics.pairwise import cosine_similarity
from model.net import load_imp_sentence_classifier,vectorizer
import numpy as np
import json
import torch
import re
from normalizer.preprocess_data import extract_sentences_from_html,process_sentence,is_noise
profile_path = r"E:\Desktop\webAutomation\utlis\profile.json"
model = load_imp_sentence_classifier("imp_sentence_classifier.pth",0.01)
model.eval()

with open(profile_path,'r',encoding='utf-8') as f:
    data = json.load(f)

def get_project_with_score(job_description, top_k=3):
    sentences = extract_sentences_from_html(job_description)

    important_sentences = []
    min_required_experience = None

    # -------- STEP 1: JD ANALYSIS --------
    for s in sentences:
        # ---- experience extraction ----
        if "experience" in s.lower() and re.search(r"\d+\+ ",s):
            nums = [int(x) for x in re.findall(r"\d+", s)]
            if nums:
                years = min(nums)
                if min_required_experience is None:
                    min_required_experience = years
                else:
                    min_required_experience = min(min_required_experience, years)

        # ---- importance classification ----
        clean_s = process_sentence(s)
        if not clean_s or is_noise(s):
            continue

        x = vectorizer.transform([clean_s]).toarray()
        x = torch.from_numpy(x).float()

        with torch.no_grad():
            pred = torch.argmax(model(x), dim=1).item()

        if pred == 1 :
            important_sentences.append(clean_s)

    if not important_sentences:
        return {"error": "No important JD sentences detected"}

    jd_vectors = vectorizer.transform(important_sentences)

    # -------- STEP 2: PROJECT SCORING --------
    project_scores = []

    for project in data["projects"]:
        bullets = [process_sentence(b) for b in project["bullets"]]
        bullets = [b for b in bullets if b]
        skills = project['skills']
        bullets.append(" ".join(skills))
        if not bullets:
            continue

        proj_vectors = vectorizer.transform(bullets)
        sims = cosine_similarity(proj_vectors, jd_vectors)

        # ATS-style score
        score = float(np.mean(np.max(sims, axis=1)))

        project_scores.append({
            "project_name": project["name"],
            "domain": project["domain"],
            "level": project["level"],
            "score": round(score * 100, 2),  # percentage-like
            "live": project.get("live"),
            "github": project.get("github")
        })

    # -------- STEP 3: TOP-K PROJECTS --------
    project_scores.sort(key=lambda x: x["score"], reverse=True)
    top_projects = project_scores[:top_k]

    # -------- STEP 4: ATS SCORE --------
    max_possible = len(important_sentences)
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



jd = "<p style=\"text-align:left\"><i>To get the best candidate experience, please consider applying for a maximum of 3 roles within 12 months to ensure you are not duplicating efforts.</i></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\">Job Category</span></p>Software Engineering<p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\">Job Details</span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\"><b><b>About Salesforce</b></b></span></p><p>Salesforce is the #1 AI CRM, where humans with agents drive customer success together. Here, ambition meets action. Tech meets trust. And innovation isn’t a buzzword — it’s a way of life. The world of work as we know it is changing and we&#39;re looking for Trailblazers who are passionate about bettering business and the world through AI, driving innovation, and keeping Salesforce&#39;s core values at the heart of it all.</p><p></p><p>Ready to level-up your career at the company leading workforce transformation in the agentic era? You’re in the right place! Agentforce is the future of AI, and you are the future of Salesforce.</p><p></p><p></p><p></p><p><b><span>Salesforce AI Research is looking for an exceptional Senior Machine Learning Engineer to help us apply and deliver cutting-edge AI to high-impact use cases. You will work on innovative AI applications and products, bringing ambitious vision to reality with advanced software engineering.</span><br /><br /><span>In your role as a Senior Machine Learning Engineer in AI Research, you will partner with researchers, applied scientists, engineers, and team members across all Cloud businesses to create AI models and solutions that transform Salesforce. </span><br /><br /><b>Your Impact:</b></b></p><ul><li><p><span>Work closely with a dedicated team of AI researchers, applied scientists, and engineers on a range of business problems and applied research</span></p></li><li><p><span>Lead the charge on taking our innovations to the next level in terms of engineering maturity and architecture</span></p></li><li><p><span>Refine and develop new AI-powered products, workflows, tools, and automation</span></p></li><li><p><span>Build tools to monitor or measure data pipelines, data quality, and models</span></p></li><li><p><span>Establish best practices with coding standards, workflows, tools, and product automation</span></p></li><li><p><span>Review and maintain existing tool-set and codebase (pipelines, models, algorithms); continue to improve existing tools and build new ones</span></p></li><li><p><span>Scale the operations of the team by building automation and libraries</span></p></li></ul><p><b><b>Required Skills:</b></b></p><p></p><ul><li><p><span>2&#43; years of industry experience and a passion for crafting, analyzing, and deploying AI-based solutions</span></p></li><li><p><span>Proficient in using Python and common AI/ML frameworks (e.g., TensorFlow, PyTorch, DeepSpeed, vLLM, or similar) and AI tools to implement models and algorithms.</span></p></li><li><p><span>Demonstrated experience with actually shipping code, getting AI/ML into production.</span></p></li><li><p><span>Experience with AI model training and model serving</span></p></li><li><p><span>Experience designing, building and optimizing AI model and data pipelines</span></p></li><li><p><span>Strong understanding of AI and Machine Learning, spanning basic AI foundations, project lifecycle, and associated challenges</span></p></li><li><p><span>Proficient at writing good quality, well-documented and tested, scalable code</span></p></li><li><p><span>Strong communication skills and ability to interface well with other engineers, researchers, and product managers</span></p></li><li><p><span>Independent, self-starter attitude</span></p></li></ul><p><b><b>Nice to have:</b></b></p><ul><li><p><span>Experience in working in a research environment</span></p></li><li><p><span>M.S. in a related technical field such as Computer Science, Machine Learning, Artificial Intelligence, Data Science, Engineering, or similar.</span></p></li></ul><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\">Unleash Your Potential</span></p><p style=\"text-align:left\"><span>When you join Salesforce, you’ll be limitless in all areas of your life. Our benefits and resources support you to find balance and<span> </span></span><i>be your best</i><span>, and our AI agents accelerate your impact so you can<span> </span></span><i>do your best</i><span>. Together, we’ll bring the power of Agentforce to organizations of all sizes and deliver amazing experiences that customers love. Apply today to not only shape the future — but to redefine what’s possible — for yourself, for AI, and the world.</span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\">Accommodations</span></p><p style=\"text-align:left\"><span>If you require assistance due to a disability applying for open positions please submit a request via this </span><a href=\"https://careers.mail.salesforce.com/accommodations-request-form\" target=\"_blank\">Accommodations Request Form</a>.</p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:left\"><span class=\"emphasis-3\">Posting Statement</span></p><p style=\"text-align:left\"><span><span>Salesforce is an equal opportunity employer and maintains a policy of non-discrimination with all employees and applicants for employment. What does that mean exactly? It means that at Salesforce, we believe in equality for all. And we believe we can lead the path to equality in part by creating a workplace that’s inclusive, and free from discrimination. </span></span><a target=\"_blank\" href=\"https://www.eeoc.gov/know-your-rights-workplace-discrimination-illegal\">Know your rights: workplace discrimination is illegal.</a><span><span> Any employee or potential employee will be assessed on the basis of merit, competence and qualifications – without regard to race, religion, color, national origin, sex, sexual orientation, gender expression or identity, transgender status, age, disability, veteran or marital status, political viewpoint, or other classifications protected by law. This policy applies to current and prospective employees, no matter where they are in their Salesforce employment journey. It also applies to recruiting, hiring, job assignment, compensation, promotion, benefits, training, assessment of job performance, discipline, termination, and everything in between. Recruiting, hiring, and promotion decisions at Salesforce are fair and based on merit. The same goes for compensation, benefits, promotions, transfers, reduction in workforce, recall, training, and education.</span></span></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p>In the United States, compensation offered will be determined by factors such as location, job level, job-related knowledge, skills, and experience. Certain roles may be eligible for incentive compensation, equity, and benefits.  Salesforce offers a variety of benefits to help you live well including: time off programs, medical, dental, vision, mental health support, paid parental leave, life and disability insurance, 401(k), and an employee stock purchasing program. More details about company benefits can be found at the following link: https://www.salesforcebenefits.com.Pursuant to the San Francisco Fair Chance Ordinance and the Los Angeles Fair Chance Initiative for Hiring, Salesforce will consider for employment qualified applicants with arrest and conviction records.<p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><h3></h3><h3></h3><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><h3></h3><h3></h3><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p>At Salesforce, we believe in equitable compensation practices that reflect the dynamic nature of labor markets across various regions.&amp;#xa;&amp;#xa;The typical base salary range for this position is $148,500 - $223,900 annually. In select cities within the San Francisco and New York City metropolitan area, the base salary range for this role is $178,900 - $246,000 annually.&amp;#xa;&amp;#xa;The range represents base salary only, and does not include company bonus, incentive for sales roles, equity or benefits, as applicable.<h3></h3><h3></h3><h3></h3><h3></h3><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p><p style=\"text-align:inherit\"></p>"
res = get_project_with_score(jd)
print(res['top_projects'])
print(res['ats_score'])
print(res['min_required_experience'])

# for x,s in imp_sent:
#     print(f"{s}\n")
# print("-----------------")
# for x in total:
#     print(x,len(imp_sent))

