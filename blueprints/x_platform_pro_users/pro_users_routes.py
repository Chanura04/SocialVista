# blueprints/twitter/routes.py

from flask import Blueprint, request, session, flash, redirect, url_for, render_template
import supabase

from werkzeug.utils import secure_filename
from database import check_user_exists, check_api_details, check_canPost, get_pg_connection, \
    update_accountUpdatedOn_column, store_instant_media_files, get_api_details, get_is_filled_api_details
from helpers import APIKeyHandler, get_current_user_fernet_key
from datetime import datetime
from celery_worker import post_instant_media_task,post_future_media_task
from decorators import has_role
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()
twitter_pro_users_bp = Blueprint('x_platform_pro_users', __name__)


@twitter_pro_users_bp.route("/pro_users_page/instant_post", methods=["POST", "GET"])
def post_instant_media_files():
    if request.method == "GET":
        # Check authentication and API details
        if not session.get("email"):
            return redirect(url_for("auth.login"))

        if not get_is_filled_api_details(session['email']):
            return redirect(url_for("api_details.connect_twitter"))

        return render_template("post_medias_f_pro_users.html",status='')

    # POST method handling
    if request.method == "POST":
        # Authentication checks
        if not session.get("email"):
            flash("⚠️ Please log in first!")
            return redirect(url_for("auth.login"))

        if not get_is_filled_api_details(session['email']):
            flash("⚠️ Please configure your API details first!")
            return redirect(url_for("api_details.connect_twitter"))

        if not (check_user_exists(session['email']) and check_canPost()):
            flash("⚠️ You don't have permission to post!")
            return redirect(url_for("x_platform_pro_users.post_instant_media_files"))

        # Get form data
        tweet_text = request.form.get("tweet_context_f_media")
        media_file = request.files.get("instant_media_file")  # This gets the actual file object

        # Validation
        if not tweet_text or not tweet_text.strip():
            flash("⚠️ Please provide tweet text!")
            return redirect(url_for("x_platform_pro_users.post_instant_media_files"))

        if not media_file or media_file.filename == '':
            flash("⚠️ Please select a media file!")
            return render_template("post_medias_f_pro_users.html", status='️⚠️  Please select a media file!')

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}
        file_extension = media_file.filename.rsplit('.', 1)[-1].lower()

        if file_extension not in allowed_extensions:
            flash(f"⚠️ Unsupported file type: {file_extension}")
            return render_template("post_medias_f_pro_users.html", status='⚠️ Unsupported file type!')

        try:

            result=get_api_details(session['email'])

            if not result:
                flash("⚠️ No API credentials found!")
                return redirect(url_for("api_details.connect_twitter"))

            # Decrypt API credentials
            fernet_key_str = get_current_user_fernet_key()
            fernet_key_bytes = fernet_key_str.encode()
            api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

            decrypt_twitter_api_key = api_key_handler_obj.decrypt_key(result[0])
            decrypt_twitter_api_secret = api_key_handler_obj.decrypt_key(result[1])
            decrypt_twitter_user_access_token = api_key_handler_obj.decrypt_key(result[2])
            decrypt_twitter_user_access_token_secret = api_key_handler_obj.decrypt_key(result[3])

            file_content = media_file.read()  # Read file content as bytes
            original_filename = media_file.filename
            content_type = media_file.content_type
            if media_file:
                post_instant_media_task.delay(session['email'],
                                        tweet_text,
                                        file_content,
                                        original_filename,content_type,
                                        file_extension,
                                        decrypt_twitter_api_key,
                                        decrypt_twitter_api_secret,
                                        decrypt_twitter_user_access_token,
                                        decrypt_twitter_user_access_token_secret)
        except Exception as e:
            print(e)


        return render_template("post_medias_f_pro_users.html",status='Successfully posted!🎉🎉')



@twitter_pro_users_bp.route("/pro_users_page/futureCase_post", methods=["POST", "GET"])
@has_role('user')
def post_futureCast_medias_f_pro_users():
    if request.method == "GET":
        # Check authentication and API details
        if not session.get("email"):
            return redirect(url_for("auth.login"))

        if not get_is_filled_api_details(session['email']):
            return redirect(url_for("api_details.connect_twitter"))

        return render_template("post_futureCast_medias_f_pro_users.html",status='')

    # POST method handling
    if request.method == "POST":
        # Authentication checks
        if not session.get("email"):
            flash("⚠️ Please log in first!")
            return redirect(url_for("auth.login"))

        if not get_is_filled_api_details(session['email']):
            flash("⚠️ Please configure your API details first!")
            return redirect(url_for("api_details.connect_twitter"))

        if not (check_user_exists(session['email']) and check_canPost()):
            flash("⚠️ You don't have permission to post!")
            return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))

        # Get form data
        tweet_text = request.form.get("tweet_context_f_futureCast_media")
        media_file = request.files.get("instant_futureCast_media_file")  # This gets the actual file object
        need_to_publish = request.form.get("future_mediaPost_time")

        # Validation
        if not tweet_text or not tweet_text.strip():
            flash("⚠️ Please provide tweet text!")
            return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))

        if not media_file or media_file.filename == '':
            flash("⚠️ Please select a media file!")
            return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))

        if not need_to_publish:
            flash("⚠️ Please select a future post date!")
            return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))


        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}
        file_extension = media_file.filename.rsplit('.', 1)[-1].lower()

        if file_extension not in allowed_extensions:
            flash(f"⚠️ Unsupported file type: {file_extension}")
            return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))

        try:

            sri_lanka_tz = ZoneInfo("Asia/Colombo")

            local_time = datetime.now(sri_lanka_tz)
            future_post_data_time = datetime.strptime(need_to_publish, "%Y-%m-%dT%H:%M")
            future_post_data_time = future_post_data_time.replace(tzinfo=sri_lanka_tz)
            check_validity = future_post_data_time >= local_time  # True if future, False if past

            result = get_api_details(session['email'])

            if not result:
                flash("⚠️ No API credentials found!")
                return redirect(url_for("api_details.connect_twitter"))

            # Decrypt API credentials
            fernet_key_str = get_current_user_fernet_key()
            fernet_key_bytes = fernet_key_str.encode()
            api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

            decrypt_twitter_api_key = api_key_handler_obj.decrypt_key(result[0])
            decrypt_twitter_api_secret = api_key_handler_obj.decrypt_key(result[1])
            decrypt_twitter_user_access_token = api_key_handler_obj.decrypt_key(result[2])
            decrypt_twitter_user_access_token_secret = api_key_handler_obj.decrypt_key(result[3])

            file_content = media_file.read()  # Read file content as bytes
            original_filename = media_file.filename
            content_type = media_file.content_type
            if media_file and check_validity:
                try:
                    post_future_media_task.apply_async(
                        args=[session['email'], need_to_publish,tweet_text,file_extension, file_content,original_filename,content_type, decrypt_twitter_api_key,
                              decrypt_twitter_api_secret, decrypt_twitter_user_access_token,
                              decrypt_twitter_user_access_token_secret], eta=future_post_data_time)
                    flash(f"🎉 Your tweet has been scheduled for {future_post_data_time}!", "success")
                    update_accountUpdatedOn_column(session['email'])

                    print(f"form data time: {need_to_publish}")
                    print(f"converted data time: {future_post_data_time}")

                    return render_template("post_futureCast_medias_f_pro_users.html", status='Successfully posted!🎉🎉 ')
                except Exception as e:

                    print(f"Error scheduling tweet: {e}")
            else:
                flash("⚠️ Please fill the required fields!")
                return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))
        except Exception as e:
            print(e)

        return redirect(url_for("x_platform_pro_users.post_futureCast_medias_f_pro_users"))






@twitter_pro_users_bp.route("/pro_users_page", methods=["POST", "GET"])
@has_role('pro_user')
def post_polls():
    pass