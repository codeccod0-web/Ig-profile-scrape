from fastapi import FastAPI
import instaloader
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IG Profile Viewer")

@app.get("/")
async def home():
    return {"message": "IG Profile API is running. Try /profile/username"}

@app.get("/profile/{username}")
async def get_profile(username: str):
    try:
        L = instaloader.Instaloader(
            # These help a bit with rate limits
            download_pictures=False,
            download_videos=False,
            download_comments=False,
            save_metadata=False
        )
        
        # === OPTIONAL LOGIN (uncomment only if needed, use throwaway account) ===
        # ig_user = os.getenv("IG_USERNAME")
        # ig_pass = os.getenv("IG_PASSWORD")
        # if ig_user and ig_pass:
        #     L.login(ig_user, ig_pass)
        
        profile = instaloader.Profile.from_username(L.context, username)
        
        return {
            "success": True,
            "username": profile.username,
            "full_name": profile.full_name,
            "bio": profile.biography,
            "followers": profile.followers,
            "following": profile.followees,
            "posts": profile.mediacount,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "profile_pic_url": profile.profile_pic_url
        }
    except instaloader.exceptions.ProfileNotExistsException:
        return {"success": False, "error": "Profile does not exist"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Optional: Add followers endpoint (but expect it to fail often on Vercel)
@app.get("/followers/{username}")
async def get_followers(username: str, limit: int = 10):
    try:
        L = instaloader.Instaloader()
        # Login strongly recommended here for followers
        profile = instaloader.Profile.from_username(L.context, username)
        followers = []
        count = 0
        for follower in profile.get_followers():
            followers.append(follower.username)
            count += 1
            if count >= limit:
                break
        return {"success": True, "username": username, "followers": followers}
    except Exception as e:
        return {"success": False, "error": str(e)}
