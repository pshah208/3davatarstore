import streamlit as st
import requests
import json
import base64
import io
from PIL import Image
import numpy as np
from typing import Dict, List, Any
import time

# Page configuration
st.set_page_config(
    page_title="StyleAI - Virtual Clothing Store",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern aesthetic
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f8f6f1 0%, #f5f2eb 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f6f1 0%, #f5f2eb 100%);
    }
    
    .clothing-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #e8e3d8;
        transition: all 0.3s ease;
    }
    
    .clothing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .avatar-preview {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e8e3d8;
    }
    
    .category-button {
        background: #d4b5a0;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .category-button:hover {
        background: #c9a68a;
        transform: scale(1.05);
    }
    
    .upload-area {
        border: 2px dashed #d4b5a0;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: rgba(212, 181, 160, 0.1);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: rgba(212, 181, 160, 0.2);
        border-color: #c9a68a;
    }
    
    .price-tag {
        background: #8b7355;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    .try-on-button {
        background: linear-gradient(45deg, #d4b5a0, #c9a68a);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 15px;
        transition: all 0.3s ease;
    }
    
    .try-on-button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(212, 181, 160, 0.4);
    }
    
    .avatar-stats {
        background: #f5f2eb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #d4b5a0;
    }
    
    h1, h2, h3 {
        color: #8b7355;
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# Gemini API configuration
GEMINI_API_KEY = "your-gemini-api-key-here"  # Replace with actual API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# Sample clothing catalog
CLOTHING_CATALOG = {
    "dresses": [
        {"id": 1, "name": "Elegant Summer Dress", "price": "$89.99", "color": "Light Blue", "size": ["XS", "S", "M", "L", "XL"], "image": "👗", "description": "Flowy summer dress perfect for casual outings"},
        {"id": 2, "name": "Formal Evening Gown", "price": "$199.99", "color": "Black", "size": ["XS", "S", "M", "L", "XL"], "image": "🖤", "description": "Sophisticated evening wear for special occasions"},
        {"id": 3, "name": "Casual Midi Dress", "price": "$65.99", "color": "Coral", "size": ["XS", "S", "M", "L", "XL"], "image": "🧡", "description": "Comfortable midi dress for everyday wear"},
    ],
    "tops": [
        {"id": 4, "name": "Silk Blouse", "price": "$79.99", "color": "White", "size": ["XS", "S", "M", "L", "XL"], "image": "👔", "description": "Premium silk blouse for professional settings"},
        {"id": 5, "name": "Casual T-Shirt", "price": "$24.99", "color": "Navy", "size": ["XS", "S", "M", "L", "XL"], "image": "👕", "description": "Comfortable cotton t-shirt for casual wear"},
        {"id": 6, "name": "Crop Top", "price": "$34.99", "color": "Pink", "size": ["XS", "S", "M", "L", "XL"], "image": "💗", "description": "Trendy crop top for summer styling"},
    ],
    "bottoms": [
        {"id": 7, "name": "High-Waist Jeans", "price": "$89.99", "color": "Dark Blue", "size": ["24", "26", "28", "30", "32", "34"], "image": "👖", "description": "Classic high-waist denim jeans"},
        {"id": 8, "name": "Pleated Skirt", "price": "$55.99", "color": "Beige", "size": ["XS", "S", "M", "L", "XL"], "image": "🟤", "description": "Elegant pleated midi skirt"},
        {"id": 9, "name": "Wide-Leg Pants", "price": "$75.99", "color": "Olive", "size": ["XS", "S", "M", "L", "XL"], "image": "🫒", "description": "Comfortable wide-leg trousers"},
    ],
    "accessories": [
        {"id": 10, "name": "Designer Handbag", "price": "$149.99", "color": "Brown", "size": ["One Size"], "image": "👜", "description": "Luxury leather handbag"},
        {"id": 11, "name": "Statement Necklace", "price": "$39.99", "color": "Gold", "size": ["One Size"], "image": "📿", "description": "Bold statement jewelry piece"},
        {"id": 12, "name": "Sunglasses", "price": "$79.99", "color": "Black", "size": ["One Size"], "image": "🕶️", "description": "UV protection designer sunglasses"},
    ]
}

class AIClothingStore:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'avatar_generated' not in st.session_state:
            st.session_state.avatar_generated = False
        if 'avatar_data' not in st.session_state:
            st.session_state.avatar_data = None
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        if 'avatar_measurements' not in st.session_state:
            st.session_state.avatar_measurements = {}
    
    def call_gemini_api(self, prompt: str, image_data: str = None) -> Dict[Any, Any]:
        """Make API call to Gemini"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        content_parts = [{"text": prompt}]
        
        if image_data:
            content_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            })
        
        payload = {
            "contents": [{
                "parts": content_parts
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        try:
            # Simulate API response for demo purposes
            if image_data:
                return {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": json.dumps({
                                    "avatar_created": True,
                                    "measurements": {
                                        "height": "5'6\"",
                                        "chest": "36\"",
                                        "waist": "28\"",
                                        "hips": "38\"",
                                        "shoulder_width": "16\"",
                                        "body_type": "Pear"
                                    },
                                    "recommended_sizes": {
                                        "tops": "M",
                                        "bottoms": "M",
                                        "dresses": "M"
                                    },
                                    "style_preferences": ["Casual", "Elegant", "Comfortable"],
                                    "color_palette": ["Earth tones", "Pastels", "Neutrals"]
                                })
                            }]
                        }
                    }]
                }
            else:
                return {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": "Fashion recommendation generated successfully."
                            }]
                        }
                    }]
                }
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return {"error": str(e)}
    
    def generate_avatar_from_image(self, uploaded_file) -> Dict[str, Any]:
        """Generate 3D avatar from uploaded image using Gemini"""
        try:
            # Convert image to base64
            image = Image.open(uploaded_file)
            image = image.convert('RGB')
            
            # Resize for API
            image.thumbnail((512, 512))
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Prompt for avatar generation
            prompt = """
            Analyze this person's photo and create a detailed 3D avatar profile. Please provide:
            1. Estimated body measurements (height, chest, waist, hips, shoulder width)
            2. Body type classification
            3. Recommended clothing sizes for tops, bottoms, and dresses
            4. Style preferences based on appearance
            5. Suitable color palette recommendations
            
            Return the response as a JSON object with the following structure:
            {
                "avatar_created": true,
                "measurements": {
                    "height": "height estimate",
                    "chest": "chest measurement",
                    "waist": "waist measurement", 
                    "hips": "hips measurement",
                    "shoulder_width": "shoulder width",
                    "body_type": "body type classification"
                },
                "recommended_sizes": {
                    "tops": "size",
                    "bottoms": "size", 
                    "dresses": "size"
                },
                "style_preferences": ["style1", "style2", "style3"],
                "color_palette": ["color1", "color2", "color3"]
            }
            """
            
            response = self.call_gemini_api(prompt, image_base64)
            
            if "candidates" in response:
                result_text = response["candidates"][0]["content"]["parts"][0]["text"]
                avatar_data = json.loads(result_text)
                return avatar_data
            else:
                return {"error": "Failed to generate avatar"}
                
        except Exception as e:
            st.error(f"Error generating avatar: {str(e)}")
            return {"error": str(e)}
    
    def get_virtual_try_on_recommendation(self, item: Dict, avatar_data: Dict) -> str:
        """Get AI recommendation for how an item would look on the avatar"""
        prompt = f"""
        Based on the avatar measurements and the clothing item details, provide a recommendation:
        
        Avatar Details:
        - Body Type: {avatar_data.get('measurements', {}).get('body_type', 'Unknown')}
        - Measurements: {json.dumps(avatar_data.get('measurements', {}))}
        - Recommended Sizes: {json.dumps(avatar_data.get('recommended_sizes', {}))}
        
        Clothing Item:
        - Name: {item['name']}
        - Description: {item['description']}
        - Available Sizes: {item['size']}
        
        Please provide:
        1. How this item would fit on this body type
        2. Recommended size for this person
        3. Style advice and how to wear it
        4. Any fit concerns or highlights
        
        Keep the response conversational and helpful, around 2-3 sentences.
        """
        
        response = self.call_gemini_api(prompt)
        if "candidates" in response:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        return "This item would look great on you! Consider trying your recommended size."
    
    def render_header(self):
        """Render the application header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #8b7355; font-size: 3rem; margin-bottom: 0;'>👗 StyleAI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #d4b5a0; font-size: 1.2rem; margin-top: 0;'>Your Personal AI Fashion Assistant</p>", unsafe_allow_html=True)
    
    def render_avatar_section(self):
        """Render the avatar creation and management section"""
        st.markdown("## 📸 Create Your 3D Avatar")
        
        if not st.session_state.avatar_generated:
            st.markdown("""
            <div class='upload-area'>
                <h3 style='color: #8b7355; margin-bottom: 10px;'>Upload Your Photo</h3>
                <p style='color: #d4b5a0;'>Upload a clear photo of yourself to create your personalized 3D avatar</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose your photo", 
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear, front-facing photo for best results"
            )
            
            if uploaded_file is not None:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(uploaded_file, caption="Your Photo", use_column_width=True)
                
                with col2:
                    if st.button("🚀 Generate 3D Avatar", key="generate_avatar"):
                        with st.spinner("Creating your 3D avatar... This may take a moment."):
                            avatar_data = self.generate_avatar_from_image(uploaded_file)
                            
                            if "error" not in avatar_data:
                                st.session_state.avatar_generated = True
                                st.session_state.avatar_data = avatar_data
                                st.session_state.avatar_measurements = avatar_data.get('measurements', {})
                                st.success("✨ Avatar created successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to create avatar. Please try again.")
        else:
            self.render_avatar_display()
    
    def render_avatar_display(self):
        """Display the generated avatar information"""
        st.markdown("### 🎯 Your Virtual Avatar")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class='avatar-preview'>
                <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f6f1, #f5f2eb); border-radius: 10px;'>
                    <div style='font-size: 4rem; margin-bottom: 10px;'>🧍‍♀️</div>
                    <h4 style='color: #8b7355; margin: 0;'>Your 3D Avatar</h4>
                    <p style='color: #d4b5a0; margin: 5px 0;'>Ready for virtual try-ons!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            measurements = st.session_state.avatar_data.get('measurements', {})
            recommended_sizes = st.session_state.avatar_data.get('recommended_sizes', {})
            
            st.markdown(f"""
            <div class='avatar-stats'>
                <h4 style='color: #8b7355; margin-top: 0;'>📏 Your Measurements</h4>
                <p><strong>Height:</strong> {measurements.get('height', 'N/A')}</p>
                <p><strong>Body Type:</strong> {measurements.get('body_type', 'N/A')}</p>
                <p><strong>Recommended Sizes:</strong></p>
                <ul>
                    <li>Tops: {recommended_sizes.get('tops', 'N/A')}</li>
                    <li>Bottoms: {recommended_sizes.get('bottoms', 'N/A')}</li>
                    <li>Dresses: {recommended_sizes.get('dresses', 'N/A')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔄 Create New Avatar", key="new_avatar"):
            st.session_state.avatar_generated = False
            st.session_state.avatar_data = None
            st.rerun()
    
    def render_clothing_catalog(self):
        """Render the clothing catalog with categories"""
        st.markdown("## 🛍️ Clothing Catalog")
        
        # Category selection
        categories = list(CLOTHING_CATALOG.keys())
        selected_category = st.selectbox(
            "Choose Category",
            categories,
            format_func=lambda x: x.title()
        )
        
        # Display items in selected category
        items = CLOTHING_CATALOG[selected_category]
        
        # Create grid layout
        cols = st.columns(3)
        
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                self.render_clothing_item(item)
    
    def render_clothing_item(self, item: Dict):
        """Render individual clothing item card"""
        st.markdown(f"""
        <div class='clothing-card'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 10px;'>
                {item['image']}
            </div>
            <h4 style='color: #8b7355; margin: 10px 0; text-align: center;'>{item['name']}</h4>
            <p style='color: #666; text-align: center; margin: 10px 0;'>{item['description']}</p>
            <p style='text-align: center;'><strong>Color:</strong> {item['color']}</p>
            <p style='text-align: center;'><strong>Sizes:</strong> {', '.join(item['size'])}</p>
            <div style='text-align: center;'>
                <span class='price-tag'>{item['price']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🛒 Add to Cart", key=f"cart_{item['id']}"):
                st.session_state.cart.append(item)
                st.success(f"Added {item['name']} to cart!")
        
        with col2:
            if st.session_state.avatar_generated:
                if st.button(f"👗 Virtual Try-On", key=f"tryon_{item['id']}"):
                    self.show_virtual_try_on(item)
            else:
                st.button("👗 Try-On (Create Avatar First)", disabled=True)
    
    def show_virtual_try_on(self, item: Dict):
        """Display virtual try-on results"""
        st.markdown("### 🎨 Virtual Try-On Results")
        
        with st.spinner("AI is analyzing how this item will look on you..."):
            time.sleep(2)  # Simulate processing time
            recommendation = self.get_virtual_try_on_recommendation(item, st.session_state.avatar_data)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class='avatar-preview'>
                <div style='text-align: center; padding: 20px;'>
                    <div style='font-size: 4rem; margin-bottom: 10px;'>🧍‍♀️</div>
                    <div style='font-size: 2rem; margin-bottom: 10px;'>{item['image']}</div>
                    <h4 style='color: #8b7355;'>You wearing</h4>
                    <p style='color: #d4b5a0;'>{item['name']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='avatar-stats'>
                <h4 style='color: #8b7355; margin-top: 0;'>🤖 AI Fashion Advice</h4>
                <p>{recommendation}</p>
                <hr style='border-color: #d4b5a0; opacity: 0.3;'>
                <p><strong>Recommended Size:</strong> {st.session_state.avatar_data.get('recommended_sizes', {}).get('tops' if 'top' in item['name'].lower() else 'dresses' if 'dress' in item['name'].lower() else 'bottoms', 'M')}</p>
                <p><strong>Fit Prediction:</strong> Perfect fit for your {st.session_state.avatar_data.get('measurements', {}).get('body_type', 'body type')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with cart and user info"""
        with st.sidebar:
            st.markdown("### 🛒 Shopping Cart")
            
            if st.session_state.cart:
                total_price = 0
                for item in st.session_state.cart:
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f"Price: {item['price']}")
                    price_value = float(item['price'].replace('$', ''))
                    total_price += price_value
                    st.markdown("---")
                
                st.markdown(f"**Total: ${total_price:.2f}**")
                
                if st.button("🚀 Checkout"):
                    st.success("Thank you for your purchase! 🎉")
                    st.session_state.cart = []
                    st.rerun()
                
                if st.button("🗑️ Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            else:
                st.markdown("Your cart is empty")
            
            st.markdown("---")
            
            # Avatar info in sidebar
            if st.session_state.avatar_generated:
                st.markdown("### 👤 Your Avatar")
                measurements = st.session_state.avatar_data.get('measurements', {})
                st.markdown(f"**Body Type:** {measurements.get('body_type', 'N/A')}")
                st.markdown(f"**Height:** {measurements.get('height', 'N/A')}")
                
                style_prefs = st.session_state.avatar_data.get('style_preferences', [])
                if style_prefs:
                    st.markdown("**Style Preferences:**")
                    for pref in style_prefs:
                        st.markdown(f"• {pref}")
            else:
                st.markdown("### 👤 Create Your Avatar")
                st.markdown("Upload a photo to get started with personalized recommendations!")
    
    def run(self):
        """Main application runner"""
        self.render_header()
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2 = st.tabs(["🏠 Home & Avatar", "🛍️ Shop"])
        
        with tab1:
            self.render_avatar_section()
            
            # Feature highlights
            if not st.session_state.avatar_generated:
                st.markdown("---")
                st.markdown("## ✨ Features")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>📸</div>
                        <h4 style='color: #8b7355;'>3D Avatar Creation</h4>
                        <p>Upload your photo and get a personalized 3D avatar with accurate measurements</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>👗</div>
                        <h4 style='color: #8b7355;'>Virtual Try-On</h4>
                        <p>See how clothes will look on your avatar before making a purchase</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div class='clothing-card' style='text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 15px;'>🤖</div>
                        <h4 style='color: #8b7355;'>AI Recommendations</h4>
                        <p>Get personalized style advice powered by advanced AI technology</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            self.render_clothing_catalog()

# Run the application
if __name__ == "__main__":
    app = AIClothingStore()
    app.run()
