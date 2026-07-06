import random
from django.core.management.base import BaseCommand
from accounts.models import Creator
from posts.models import Post
from social.models import Follow


SAMPLE_CONTENT = [
    "Just shipped a new feature!",
    "Working on system design fundamentals today.",
    "Coffee first, code second.",
    "Anyone else debugging Postgres indexes tonight?",
    "New track dropping this week.",
    "Load testing is oddly satisfying.",
    "Docker containers are finally behaving.",
    "Learning about fan-out strategies in feed systems.",
    "NGINX config finally clicked for me.",
    "Redis caching saved my API response times.",
]


class Command(BaseCommand):
    help = "Seed bulk fake users, follows, and posts for feed load testing"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=50)
        parser.add_argument("--posts", type=int, default=5000)

    def handle(self, *args, **options):
        num_users = options["users"]
        num_posts = options["posts"]

        self.stdout.write(f"Creating {num_users} fake users...")
        existing_handles = set(Creator.objects.values_list("handle", flat=True))
        new_users = []
        for i in range(num_users):
            handle = f"testuser{i}"
            if handle in existing_handles:
                continue
            new_users.append(
                Creator(
                    username=handle,
                    handle=handle,
                    email=f"{handle}@example.com",
                    role="creator",
                )
            )
        Creator.objects.bulk_create(new_users, batch_size=500)

        all_users = list(Creator.objects.all())
        self.stdout.write(self.style.SUCCESS(f"Total users now: {len(all_users)}"))

        self.stdout.write("Creating follow relationships...")
        follows_to_create = []
        seen_pairs = set()
        for user in all_users:
            follow_count = random.randint(5, 20)
            possible_targets = [u for u in all_users if u.id != user.id]
            targets = random.sample(possible_targets, min(follow_count, len(possible_targets)))
            for target in targets:
                pair = (user.id, target.id)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    follows_to_create.append(Follow(follower=user, following=target))

        Follow.objects.bulk_create(follows_to_create, batch_size=500, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Created {len(follows_to_create)} follow relationships"))

        self.stdout.write(f"Creating {num_posts} fake posts...")
        posts_to_create = []
        for _ in range(num_posts):
            author = random.choice(all_users)
            content = random.choice(SAMPLE_CONTENT)
            posts_to_create.append(Post(author=author, content=content, post_type="text"))

        Post.objects.bulk_create(posts_to_create, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"Done. Total posts: {Post.objects.count()}"))