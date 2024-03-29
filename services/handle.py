import os
import base64
import cloudinary
import cloudinary.uploader as CloudinaryUploader
from cloudinary import CloudinaryImage
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Load Cloudinary configuration from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

class HandleImage():
    def upload(self, request):
        # Get the image file from the request
        imageURL = request.form.get("url")
        filename = request.files.get("filename")
        imageResponse = requests.get(imageURL)
        if(imageResponse.status_code == 200):
            imageBase64 = "data:image/jpg;base64," + base64.b64encode(imageResponse.content).decode('utf-8')
        # Upload the image to Cloudinary
        response = CloudinaryUploader.upload(file=imageBase64, public_id=filename)

        # Extract the public_id and url from the response
        publicId = response.get("public_id")
        url = response.get("secure_url")
        return {'public_id': publicId, 'format': format, 'url_upload': url}



    def transfer(self, imageCloudinary, request):
        options = [request.form.to_dict()]
        
        contentText = request.form.get('insert_text')
        #   Syntax: {font}:{font-family},{size}:{font_size},{color}:{code_color},{weight}:{font_weight},{style}:{font_style},{opacity}:{opacity},{is_underline}:{Boolean},{position}:{position},{x}:{x_offset},{y}:{y_offset}
        styleText = request.form.get('style_text')
        contentImage = request.form.get('insert_image')
        #   Syntax: 
        styleImage = request.form.get('style_image')
        if(contentText):
            options = self._insertText(contentText, styleText)
            
        # if(contentImage):
        #     options += self._insertImage(contentImage, styleImage)

        cloudinaryImage = CloudinaryImage(imageCloudinary['public_id'])
        cloudinaryImage = cloudinaryImage.build_url(transformation = options)

        return cloudinaryImage
    
    """
    Convert position for text or image in layer
    """
    def _convertPosition(self, positionText):
        positionList = {
            'top_left': "north_west",
            'top': "north",
            'top_right': "north_east",
            'left': "west",
            'center': "center",
            'right': "east",
            'bottom_left': "south_west",
            'bottom': "south",
            'bottom_right': "south_east",
        }
        return positionList.get(positionText)

    """ 
    Feature: Parse style.
    @param styles:{string}
    """
    def _parseStyle(self, styles):
        parsedDict = {}
        styleArr = styles.split(',')
        for style in styleArr:
            key, value = style.split(':')
            value = value.strip('"')
            parsedDict[key] = value

        return parsedDict
    
    def _parseFontStyle(self, fontStyle):
        optionStyle = {}
        styleArr = {
            "bold": "font_weight",
            "italic": "font_style",
            "underline": "text_decoration",
        }
        fontStyleArr = fontStyle.split('_')
        for style in fontStyleArr:
            if(style in styleArr):
                styleKey = styleArr.get(style)
                optionStyle[style] = styleKey

        return optionStyle
    
    """ 
    Feature: Insert text in original image
    @param text:{string}
    @param styleText:{string}
    """
    def _insertText(self, text, styleText):
        styles = self._parseStyle(styleText)
        fontStyles = self._parseFontStyle(styles.get('style'))
        options = [
            {
               "color": styles.get('color', "#000000"),
               "overlay": {
                   "font_family": styles.get('font', "arial"),
                   "font_size": styles.get('size', 12),
                   "text": text,
                   **fontStyles,
                },
            },
            {
                "opacity": styles.get('opacity', 100),
            },
            {
                "flags": "layer_apply",
                "gravity": self._convertPosition(styles.get('position')),
                "x": styles.get('x'),
                "y": styles.get('y'),
            }
        ]

        return options
    
    """ 
    Insert image in original image
    @param contentImage:{string}
    @param styleImage:{string}
    """
    def _insertImage(self, contentImage, styleImage):
        styles = self._parseStyle(styleImage)
        return [
            {'overlay': contentImage['public_id']},
            {
                'flags': "layer_apply",
                'gravity': self._convertPosition(styles.get('position')),
            },
        ]

