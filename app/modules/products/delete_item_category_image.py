from flask import Blueprint, jsonify, request
from modules.security.permission_required import permission_required
from modules.security.routines.get_user_and_db_details import get_user_and_db_details
from config import DELETE_ACCESS_TYPE
from modules.utilities.logger import logger

# Define the Blueprint for deleting item images API
delete_item_category_images_api = Blueprint('delete_item_category_images_api', __name__)

@delete_item_category_images_api.route('/delete_item_category_image', methods=['DELETE'])
@permission_required(DELETE_ACCESS_TYPE, __file__)
def delete_item_category_image():
    authorization_header = request.headers.get('Authorization')

    try:
        company, instance, dbuser, mydb1, appuser, appuserid, user_info, employee_info = get_user_and_db_details(authorization_header)
        logger.debug(f"{appuser} --> {__name__}: Successfully retrieved user details from the token.")
    except ValueError as e:
        logger.error(f"Failed to retrieve user details from token. Error: {str(e)}")
        return jsonify({"error": str(e)}), 401
    
    if not appuser:
        logger.error(f"Unauthorized access attempt: {appuser} --> {__name__}: Application user not found.")
        return jsonify({"error": "Unauthorized. Username not found."}), 401

    logger.debug(f"{appuser} --> {__name__}: Entered in the delete item image function")

    # Retrieve category_id and image_id from request.args
    category_id = request.args.get('category_id')  # Use request.args for GET/DELETE queries
    image_id = request.args.get('image_id')

    logger.debug(f"{appuser} --> {__name__}: Received Parameters category_id and image_id {category_id}, {image_id}")

    if not category_id or not image_id:
        return jsonify({'error': 'category_id and image_id are required'}), 400

    try:
        mycursor = mydb1.cursor()

        # Check if the category_id and image_id exist in the mapping table
        mapping_check_query = """
            SELECT COUNT(*) FROM com.category_image_mapping 
            WHERE category_id = %s AND image_id = %s
        """
        mycursor.execute(mapping_check_query, (category_id, image_id))
        if mycursor.fetchone()[0] == 0:
            return jsonify({'error': 'category_id or image_id not found in the mapping table'}), 404

        # Fetch the current image order (before deletion)
        fetch_order_query = """
            SELECT image_id, image_order
            FROM com.category_image_mapping
            WHERE category_id = %s
            ORDER BY image_order
        """
        mycursor.execute(fetch_order_query, (category_id,))
        image_order_map = mycursor.fetchall()

        # Delete the image from com.category_imagestable
        delete_image_query = """
            DELETE FROM com.category_images
            WHERE image_id = %s
        """
        mycursor.execute(delete_image_query, (image_id,))

        # Delete the mapping from com.category_image_mapping
        delete_mapping_query = """
            DELETE FROM com.category_image_mapping 
            WHERE category_id = %s AND image_id = %s
        """
        mycursor.execute(delete_mapping_query, (category_id, image_id))

        # Fetch the remaining images for reordering after deletion
        fetch_remaining_images_query = """
            SELECT image_id
            FROM com.category_image_mapping
            WHERE category_id = %s
            ORDER BY image_order
        """
        mycursor.execute(fetch_remaining_images_query, (category_id,))
        remaining_images = mycursor.fetchall()

        # Reorder the remaining images starting from 1
        new_order = 1
        update_order_query = """
            UPDATE com.category_image_mapping
            SET image_order = %s
            WHERE category_id = %s AND image_id = %s
        """

        for img in remaining_images:
            mycursor.execute(update_order_query, (new_order, category_id, img[0]))
            new_order += 1

        mydb1.commit()

        logger.debug(f"{appuser} --> {__name__}: Image order successfully re-sequenced for category_id {category_id}")
        logger.info(f"{appuser} --> {__name__}: Image successfully deleted for category_id={category_id}, image_id={image_id} and image order reset")

        return jsonify({'message': 'Image successfully deleted and image order reset.'}), 200

    except Exception as e:
        logger.error(f"{appuser} --> {__name__}: Failed to delete image: {str(e)}")
        return jsonify({'error': 'Failed to delete image.', 'details': str(e)}), 500

    finally:
        if mycursor:
            mycursor.close()
        if mydb1:
            mydb1.close()
