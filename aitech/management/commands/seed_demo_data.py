from datetime import date
from io import BytesIO

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from aitech.models import (
    Service, ServiceFeature, SupportingService, Testimonial,
    ProjectCategory, PortfolioProject, ResultStatistic, ContactInfo,
)


def download_image(photo_id, width=900):
    """Fetch a free-license Unsplash photo. Returns None on any failure so callers can fall back."""
    url = f"https://images.unsplash.com/photo-{photo_id}?w={width}&q=80&fit=crop"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return ContentFile(response.content)
    except requests.RequestException:
        return None


def hex_to_rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def make_placeholder_image(title, start_hex, end_hex, size=(900, 600)):
    start = hex_to_rgb(start_hex)
    end = hex_to_rgb(end_hex)
    width, height = size
    img = Image.new('RGB', size, start)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        t = y / height
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw.rectangle([(0, height - 110), (width, height)], fill=(0, 0, 0, 120))
    draw.text((36, height - 80), title, fill=(255, 255, 255))

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=87)
    return ContentFile(buffer.getvalue())


CATEGORIES = [
    dict(name="Healthcare AI", slug="healthcare-ai", icon="fas fa-heart-pulse", color="#4361ee",
         description="Medical imaging analysis, diagnostics support, and patient care optimization powered by AI."),
    dict(name="Financial Services", slug="financial-services", icon="fas fa-chart-line", color="#4cc9f0",
         description="Fraud detection, risk modeling, and algorithmic trading systems built for scale and compliance."),
    dict(name="Retail & E-commerce", slug="retail-ecommerce", icon="fas fa-cart-shopping", color="#f72585",
         description="Demand forecasting, personalization engines, and inventory optimization for modern retail."),
    dict(name="Manufacturing & IoT", slug="manufacturing-iot", icon="fas fa-industry", color="#7209b7",
         description="Predictive maintenance and computer-vision quality control for industrial operations."),
    dict(name="Logistics & Supply Chain", slug="logistics-supply-chain", icon="fas fa-truck-fast", color="#3a0ca3",
         description="Route optimization, warehouse automation, and demand-driven supply chain planning."),
]

SERVICES = [
    dict(title="Machine Learning Development", slug="machine-learning-development", icon="fa-brain",
         category="Predictive Analytics", gradient_start="#4361ee", gradient_end="#3a0ca3", badge_color="#4cc9f0",
         description="We design, train, and deploy custom machine learning models tailored to your business "
                      "data and objectives, from forecasting to recommendation systems.",
         short_description="Custom ML models built and deployed for your specific business problem.",
         features=["Custom model architecture", "Feature engineering", "Model monitoring", "A/B testing"]),
    dict(title="Natural Language Processing", slug="natural-language-processing", icon="fa-comments",
         category="Text Intelligence", gradient_start="#4cc9f0", gradient_end="#4361ee", badge_color="#4361ee",
         description="Extract meaning from text at scale with sentiment analysis, entity extraction, "
                      "summarization, and conversational AI tailored to your domain.",
         short_description="Sentiment analysis, summarization, and conversational AI for your text data.",
         features=["Sentiment analysis", "Document summarization", "Entity extraction", "Chatbot development"]),
    dict(title="Computer Vision Solutions", slug="computer-vision-solutions", icon="fa-eye",
         category="Visual Intelligence", gradient_start="#f72585", gradient_end="#7209b7", badge_color="#f72585",
         description="From defect detection to visual search, we build computer vision pipelines that "
                      "turn images and video into actionable business insight.",
         short_description="Image and video AI for detection, classification, and quality control.",
         features=["Object detection", "Image classification", "Quality inspection", "Video analytics"]),
    dict(title="Data Analytics & BI", slug="data-analytics-bi", icon="fa-chart-column",
         category="Business Intelligence", gradient_start="#7209b7", gradient_end="#3a0ca3", badge_color="#7209b7",
         description="Turn raw data into decisions with modern data pipelines, dashboards, and predictive "
                      "analytics built on a solid data engineering foundation.",
         short_description="Data pipelines and dashboards that turn raw data into decisions.",
         features=["Data pipeline design", "Interactive dashboards", "Predictive analytics", "KPI reporting"]),
    dict(title="MLOps & Model Deployment", slug="mlops-model-deployment", icon="fa-server",
         category="AI Infrastructure", gradient_start="#3a0ca3", gradient_end="#4361ee", badge_color="#4cc9f0",
         description="We productionize models with CI/CD pipelines, monitoring, and scalable serving "
                      "infrastructure so your AI investments stay reliable in production.",
         short_description="Production-grade infrastructure to deploy and monitor your AI models.",
         features=["CI/CD for ML", "Model versioning", "Scalable serving", "Drift monitoring"]),
    dict(title="Generative AI & LLM Solutions", slug="generative-ai-llm-solutions", icon="fa-wand-magic-sparkles",
         category="Generative AI", gradient_start="#4361ee", gradient_end="#4cc9f0", badge_color="#4361ee",
         description="From retrieval-augmented chatbots to content generation tools, we build practical "
                      "products on top of modern large language models.",
         short_description="RAG chatbots, copilots, and content tools built on modern LLMs.",
         features=["RAG chatbots", "Prompt engineering", "Fine-tuning", "LLM evaluation"]),
]

SUPPORTING_SERVICES = [
    dict(title="AI Strategy & Roadmapping", icon="fa-map", badge_text="Planning",
         gradient_start="#4361ee", gradient_end="#3a0ca3", badge_color="#4361ee",
         description="Identify high-impact AI opportunities and build a roadmap aligned with business goals."),
    dict(title="Integration & Deployment", icon="fa-plug", badge_text="Deployment",
         gradient_start="#4cc9f0", gradient_end="#4361ee", badge_color="#4cc9f0",
         description="Seamlessly integrate AI solutions into your existing systems with reliable deployment."),
    dict(title="Team Training & Enablement", icon="fa-graduation-cap", badge_text="Education",
         gradient_start="#f72585", gradient_end="#7209b7", badge_color="#f72585",
         description="Upskill your team with hands-on AI training tailored to your tools and workflows."),
]

TESTIMONIALS = [
    dict(name="Sarah Johnson", role="CEO", company="TechInnovate", rating=5,
         text="AI Tech transformed our business operations with a machine learning platform that paid for "
              "itself within two quarters."),
    dict(name="Michael Chen", role="Operations Director", company="GlobalRetail", rating=5,
         text="Their forecasting models gave us visibility into demand we never had before. Genuinely "
              "changed how we plan inventory."),
    dict(name="Priya Nair", role="CTO", company="MedCore Diagnostics", rating=5,
         text="The computer vision pipeline they built cut our image review time by more than half without "
              "sacrificing accuracy."),
    dict(name="David Alvarez", role="VP of Engineering", company="FinEdge Capital", rating=4,
         text="Professional, communicative, and technically excellent. Our fraud detection false-positive "
              "rate dropped significantly."),
    dict(name="Emma Williams", role="Head of Data", company="Northwind Logistics", rating=5,
         text="From strategy to deployment, the team felt like an extension of ours. The MLOps setup they "
              "left us with is rock solid."),
]

PORTFOLIO_PROJECTS = [
    dict(title="Predictive Diagnostics Platform", category_slug="healthcare-ai", client="MedCore Diagnostics",
         technologies="Python, TensorFlow, FastAPI, AWS", is_featured=True, date=date(2025, 3, 10),
         photo_id="1551190822-a9333d879b1f",
         description="A medical imaging platform that flags anomalies for radiologist review, reducing "
                      "average review time by 55% while maintaining diagnostic accuracy.",
         short_description="AI-assisted medical imaging review platform for faster, consistent diagnostics."),
    dict(title="Real-Time Fraud Detection Engine", category_slug="financial-services", client="FinEdge Capital",
         technologies="Python, PyTorch, Kafka, Kubernetes", is_featured=True, date=date(2025, 1, 22),
         photo_id="1611974789855-9c2a0a7236a3",
         description="A streaming fraud detection system processing millions of transactions daily with "
                      "sub-100ms scoring latency and continuous model retraining.",
         short_description="Streaming fraud detection with sub-100ms scoring and continuous retraining."),
    dict(title="Demand Forecasting & Personalization Suite", category_slug="retail-ecommerce", client="GlobalRetail",
         technologies="Python, Scikit-learn, Airflow, Snowflake", is_featured=True, date=date(2024, 11, 5),
         photo_id="1441986300917-64674bd600d8",
         description="A forecasting and personalization suite that improved inventory turnover and increased "
                      "conversion through tailored product recommendations.",
         short_description="Forecasting and personalization engine driving better inventory and conversion."),
    dict(title="Automated Visual Quality Inspection", category_slug="manufacturing-iot", client="Novasteel Industrial",
         technologies="Python, OpenCV, YOLO, Edge devices", is_featured=False, date=date(2024, 9, 18),
         photo_id="1516937941344-00b4e0337589",
         description="An edge-deployed computer vision system that inspects products on the line, catching "
                      "defects human inspectors were missing under time pressure.",
         short_description="Edge computer vision for real-time production line quality control."),
    dict(title="Warehouse Route Optimization Engine", category_slug="logistics-supply-chain", client="Northwind Logistics",
         technologies="Python, OR-Tools, PostgreSQL, React", is_featured=False, date=date(2024, 7, 2),
         photo_id="1494412651409-8963ce7935a7",
         description="An optimization engine that reduced average delivery route length by 18% across a "
                      "regional distribution network.",
         short_description="Route optimization system cutting average delivery distance by 18%."),
    dict(title="Conversational Support Copilot", category_slug="retail-ecommerce", client="ShopWave",
         technologies="Python, LangChain, OpenAI API, Redis", is_featured=False, date=date(2025, 5, 14),
         photo_id="1553775282-20af80779df7",
         description="A retrieval-augmented support assistant that resolves common customer queries "
                      "instantly and escalates complex cases with full conversation context.",
         short_description="RAG-based support copilot resolving common queries automatically."),
]

RESULT_STATS = [
    dict(title="Projects Delivered", value="150+", icon="fas fa-diagram-project",
         description="AI and data science projects delivered across industries."),
    dict(title="Client Satisfaction Rate", value="98%", icon="fas fa-face-smile",
         description="Average client satisfaction across delivered engagements."),
    dict(title="AI & Data Specialists", value="40+", icon="fas fa-users",
         description="Engineers, data scientists, and ML specialists on the team."),
    dict(title="Years of Combined Experience", value="10+", icon="fas fa-award",
         description="Combined industry experience across the core team."),
]


class Command(BaseCommand):
    help = "Replace placeholder/test rows with realistic demo content for the AI Tech site."

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-existing', action='store_true',
            help="Add demo data without deleting current Service/Testimonial/ProjectCategory rows.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options['keep_existing']:
            self.stdout.write("Clearing existing services, testimonials, categories, and portfolio content...")
            ServiceFeature.objects.all().delete()
            Service.objects.all().delete()
            SupportingService.objects.all().delete()
            Testimonial.objects.all().delete()
            PortfolioProject.objects.all().delete()
            ProjectCategory.objects.all().delete()
            ResultStatistic.objects.all().delete()

        self.stdout.write("Creating project categories...")
        categories_by_slug = {}
        for entry in CATEGORIES:
            category = ProjectCategory.objects.create(**entry)
            categories_by_slug[entry['slug']] = category

        self.stdout.write("Creating services and features...")
        for entry in SERVICES:
            features = entry.pop('features')
            service = Service.objects.create(**entry)
            for order, name in enumerate(features):
                ServiceFeature.objects.create(service=service, name=name, order=order)

        self.stdout.write("Creating supporting services...")
        for order, entry in enumerate(SUPPORTING_SERVICES):
            SupportingService.objects.create(order=order, **entry)

        self.stdout.write("Creating testimonials...")
        for entry in TESTIMONIALS:
            Testimonial.objects.create(**entry)

        self.stdout.write("Creating portfolio projects with real photography...")
        for order, entry in enumerate(PORTFOLIO_PROJECTS):
            category = categories_by_slug[entry.pop('category_slug')]
            photo_id = entry.pop('photo_id', None)
            image_file = download_image(photo_id) if photo_id else None
            if image_file is None:
                self.stdout.write(self.style.WARNING(
                    f"  Could not download photo for '{entry['title']}', using generated placeholder."
                ))
                image_file = make_placeholder_image(entry['title'], category.color, "#0d0d18")
            project = PortfolioProject(
                title=entry['title'],
                description=entry['description'],
                short_description=entry['short_description'],
                category=category,
                client=entry['client'],
                project_date=entry['date'],
                technologies=entry['technologies'],
                is_featured=entry['is_featured'],
                order=order,
            )
            project.image.save(f"{project.title[:40]}.jpg", image_file, save=True)

        self.stdout.write("Creating result statistics...")
        for order, entry in enumerate(RESULT_STATS):
            ResultStatistic.objects.create(order=order, **entry)

        if not ContactInfo.objects.exists():
            self.stdout.write("Creating company contact info...")
            ContactInfo.objects.create(
                company_name="AI Tech",
                phone="+1 (555) 123-4567",
                email="info@aitech.com",
                address="123 AI Street, Tech City, TC 10101",
                location="Tech City, TC",
                facebook="https://facebook.com",
                linkedin="https://linkedin.com",
                twitter="https://twitter.com",
                instagram="https://instagram.com",
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
