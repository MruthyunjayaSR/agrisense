-- ==============================================================================
-- AGRISENSE DATABASE SCHEMA & SUPABASE MIGRATION
-- Project: AgriSense – AI-Powered Smart Agriculture Platform
-- Database: Supabase PostgreSQL with Row Level Security (RLS)
-- ==============================================================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. PROFILES TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(30),
    location VARCHAR(255),
    district VARCHAR(100),
    state VARCHAR(100),
    preferred_language VARCHAR(20) DEFAULT 'en',
    farmer_experience_level VARCHAR(30) DEFAULT 'Beginner', -- 'Beginner', 'Intermediate', 'Expert'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 2. FARMS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    farm_name VARCHAR(150) NOT NULL,
    land_area NUMERIC(10, 2) NOT NULL,
    area_unit VARCHAR(20) DEFAULT 'Acres', -- 'Acres', 'Hectares', 'Guntas'
    soil_type VARCHAR(100), -- 'Alluvial', 'Black', 'Red', 'Laterite', 'Sandy Loam'
    soil_n NUMERIC(6, 2), -- Nitrogen (kg/ha)
    soil_p NUMERIC(6, 2), -- Phosphorus (kg/ha)
    soil_k NUMERIC(6, 2), -- Potassium (kg/ha)
    soil_ph NUMERIC(4, 2), -- pH 0-14
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 3. CROPS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    farm_id UUID REFERENCES public.farms(id) ON DELETE SET NULL,
    crop_name VARCHAR(100) NOT NULL,
    crop_variety VARCHAR(100),
    sowing_date DATE NOT NULL,
    expected_harvest_date DATE,
    season VARCHAR(30), -- 'Kharif', 'Rabi', 'Zaid', 'Perennial'
    current_growth_stage VARCHAR(100) DEFAULT 'Sowing',
    status VARCHAR(50) DEFAULT 'Active', -- 'Active', 'Harvested', 'Damaged'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 4. CROP MONITORING TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.crop_monitoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES public.crops(id) ON DELETE CASCADE,
    observation_date DATE DEFAULT CURRENT_DATE,
    growth_stage VARCHAR(100) NOT NULL,
    health_status VARCHAR(50) DEFAULT 'Healthy', -- 'Healthy', 'Mild Stress', 'Disease Suspected', 'Pest Detected'
    notes TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 5. CROP RECOMMENDATIONS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.crop_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    input_parameters JSONB NOT NULL,
    recommended_crops JSONB NOT NULL,
    model_name VARCHAR(100) DEFAULT 'RandomForestClassifier-v1.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 6. DISEASE PREDICTIONS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.disease_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES public.crops(id) ON DELETE SET NULL,
    image_url TEXT,
    disease_name VARCHAR(150) NOT NULL,
    confidence NUMERIC(5, 2) NOT NULL,
    severity VARCHAR(50) DEFAULT 'Moderate',
    treatment_advice TEXT,
    organic_treatment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 7. PRICE PREDICTIONS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.price_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    crop_name VARCHAR(100) NOT NULL,
    market VARCHAR(150),
    current_price NUMERIC(10, 2) NOT NULL,
    forecast_data JSONB NOT NULL,
    best_selling_date VARCHAR(50),
    best_selling_price NUMERIC(10, 2),
    model_name VARCHAR(100) DEFAULT 'GradientBoosting-ARIMA-v1.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 8. CROP CALENDAR TASKS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.crop_calendar_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    crop_id UUID REFERENCES public.crops(id) ON DELETE CASCADE,
    task_name VARCHAR(200) NOT NULL,
    task_description TEXT,
    task_date DATE NOT NULL,
    growth_stage VARCHAR(100),
    task_type VARCHAR(50) DEFAULT 'care', -- 'sow', 'irrigate', 'fertilize', 'spray', 'harvest', 'care'
    priority VARCHAR(30) DEFAULT 'Medium', -- 'Low', 'Medium', 'High', 'Critical'
    status VARCHAR(30) DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Completed', 'Skipped'
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 9. WEATHER RECORDS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.weather_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    location VARCHAR(200) NOT NULL,
    temperature NUMERIC(5, 2),
    humidity NUMERIC(5, 2),
    rainfall NUMERIC(6, 2),
    wind_speed NUMERIC(5, 2),
    forecast_data JSONB,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 10. NOTIFICATIONS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'General', -- 'Irrigation', 'Fertilizer', 'Weather Alert', 'Price Alert', 'Disease Alert'
    is_read BOOLEAN DEFAULT FALSE,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 11. CHATBOT HISTORY TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chatbot_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 12. MARKET DEAL REQUESTS TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.market_deal_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    company_name VARCHAR(200) NOT NULL,
    farmer_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    location VARCHAR(200) NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    crop_variety VARCHAR(100),
    quantity NUMERIC(10, 2) NOT NULL,
    expected_price NUMERIC(10, 2) NOT NULL,
    message TEXT,
    status VARCHAR(30) DEFAULT 'Pending', -- 'Pending', 'Contacted', 'Agreed', 'Completed', 'Rejected'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 13. GOVERNMENT SCHEMES TABLE (Reference Table, Public Read)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.government_schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheme_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    benefits TEXT NOT NULL,
    official_url VARCHAR(255) NOT NULL,
    required_documents TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================================
-- INDEXES FOR PERFORMANCE
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_farms_user_id ON public.farms(user_id);
CREATE INDEX IF NOT EXISTS idx_crops_user_id ON public.crops(user_id);
CREATE INDEX IF NOT EXISTS idx_crops_farm_id ON public.crops(farm_id);
CREATE INDEX IF NOT EXISTS idx_crop_mon_crop_id ON public.crop_monitoring(crop_id);
CREATE INDEX IF NOT EXISTS idx_cal_tasks_crop_id ON public.crop_calendar_tasks(crop_id);
CREATE INDEX IF NOT EXISTS idx_cal_tasks_user_date ON public.crop_calendar_tasks(user_id, task_date);
CREATE INDEX IF NOT EXISTS idx_disease_user_id ON public.disease_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_price_pred_crop ON public.price_predictions(crop_name);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON public.notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_chatbot_user ON public.chatbot_history(user_id);

-- ==============================================================================
-- AUTOMATIC PROFILE TRIGGER (ON Supabase auth.users INSERT)
-- ==============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, first_name, last_name, email, phone, farmer_experience_level, preferred_language)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'first_name', split_part(COALESCE(NEW.email, 'Farmer'), '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
        COALESCE(NEW.email, ''),
        COALESCE(NEW.raw_user_meta_data->>'phone', NEW.phone, ''),
        COALESCE(NEW.raw_user_meta_data->>'farmer_experience_level', 'Beginner'),
        COALESCE(NEW.raw_user_meta_data->>'preferred_language', 'en')
    )
    ON CONFLICT (id) DO UPDATE SET
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        phone = COALESCE(EXCLUDED.phone, public.profiles.phone),
        updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger definition for auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.farms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crops ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crop_monitoring ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crop_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.disease_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.price_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crop_calendar_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chatbot_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_deal_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.government_schemes ENABLE ROW LEVEL SECURITY;

-- 1. Profiles Policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- 2. Farms Policies
CREATE POLICY "Users can view own farms" ON public.farms
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own farms" ON public.farms
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own farms" ON public.farms
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own farms" ON public.farms
    FOR DELETE USING (auth.uid() = user_id);

-- 3. Crops Policies
CREATE POLICY "Users can view own crops" ON public.crops
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own crops" ON public.crops
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own crops" ON public.crops
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own crops" ON public.crops
    FOR DELETE USING (auth.uid() = user_id);

-- 4. Crop Monitoring Policies
CREATE POLICY "Users can view own monitoring" ON public.crop_monitoring
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own monitoring" ON public.crop_monitoring
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 5. Crop Recommendations Policies
CREATE POLICY "Users can view own recommendations" ON public.crop_recommendations
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can insert recommendations" ON public.crop_recommendations
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- 6. Disease Predictions Policies
CREATE POLICY "Users can view own disease predictions" ON public.disease_predictions
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can insert disease predictions" ON public.disease_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- 7. Price Predictions Policies
CREATE POLICY "Users can view price predictions" ON public.price_predictions
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can insert price predictions" ON public.price_predictions
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- 8. Calendar Tasks Policies
CREATE POLICY "Users can view own calendar tasks" ON public.crop_calendar_tasks
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own calendar tasks" ON public.crop_calendar_tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own calendar tasks" ON public.crop_calendar_tasks
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own calendar tasks" ON public.crop_calendar_tasks
    FOR DELETE USING (auth.uid() = user_id);

-- 9. Weather Records Policies
CREATE POLICY "Users can view weather records" ON public.weather_records
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Users can insert weather records" ON public.weather_records
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- 10. Notifications Policies
CREATE POLICY "Users can view own notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- 11. Chatbot History Policies
CREATE POLICY "Users can view own chat history" ON public.chatbot_history
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert chat history" ON public.chatbot_history
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- 12. Market Deal Requests Policies
CREATE POLICY "Users can view own deal requests" ON public.market_deal_requests
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);
CREATE POLICY "Anyone can insert deal requests" ON public.market_deal_requests
    FOR INSERT WITH CHECK (TRUE);

-- 13. Government Schemes Policies (Public read)
CREATE POLICY "Anyone can view government schemes" ON public.government_schemes
    FOR SELECT USING (TRUE);

-- ==============================================================================
-- SEED DATA: OFFICIAL GOVERNMENT SCHEMES
-- ==============================================================================
INSERT INTO public.government_schemes (scheme_name, category, description, eligibility, benefits, official_url, required_documents)
VALUES
(
    'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
    'Income Support',
    'Financial assistance scheme providing direct cash transfers to all landholding farmer families across India.',
    'All small and marginal farmer families holding cultivable land up to 2 hectares.',
    '₹6,000 per year directly transferred in three equal installments of ₹2,000 every 4 months.',
    'pmkisan.gov.in',
    'Aadhaar card, Land ownership papers, Bank account linked with Aadhaar.'
),
(
    'PM Fasal Bima Yojana (PMFBY)',
    'Crop Insurance',
    'Comprehensive risk insurance coverage to provide financial support to farmers suffering crop loss/damage arising out of unforeseen events.',
    'All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.',
    'Lowest premium rates (1.5% for Rabi, 2% for Kharif, 5% for commercial/horticultural crops) with 100% loss coverage.',
    'pmfby.gov.in',
    'Sowing certificate, Land records (7/12, RoR), Bank passbook, Aadhaar card.'
),
(
    'Kisan Credit Card (KCC) Scheme',
    'Agricultural Credit',
    'Provides adequate and timely credit support from the banking system for agricultural and other allied activities.',
    'All farmers, individual/joint borrowers, tenant farmers, oral lessees and SHGs.',
    'Short-term credit up to ₹3 Lakh at an effective subsidized interest rate of 4% per annum upon prompt repayment.',
    'myscheme.gov.in',
    'Application form, Land holding documents, Identity proof, Address proof.'
),
(
    'Soil Health Card Scheme',
    'Soil Health',
    'Provides soil health cards to farmers with customized fertilizer recommendations to optimize crop productivity and reduce input costs.',
    'All farmers holding agricultural land across all states and union territories.',
    'Free laboratory soil analysis covering 12 vital macro and micro nutrients (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC).',
    'soilhealth.dac.gov.in',
    'Aadhaar card, Mobile number, Farm plot identification details.'
),
(
    'PM Krishi Sinchayee Yojana (PMKSY)',
    'Irrigation',
    'Expands cultivable area under assured irrigation, improves on-farm water use efficiency ("Per Drop More Crop") through drip and sprinkler systems.',
    'Farmers of all categories who possess cultivable agricultural land with an accessible water source.',
    'Up to 55% subsidy for small and marginal farmers and 45% for other farmers on micro-irrigation equipment installation.',
    'pmksy.gov.in',
    'Electricity bill/water source proof, Land registry certificate, Bank passbook, Aadhaar.'
)
ON CONFLICT DO NOTHING;

-- ==============================================================================
-- STORAGE BUCKET CONFIGURATION (Execute in Supabase Storage or Dashboard)
-- Bucket: 'crop-images' (Public read for previewing uploaded leaf and crop pictures)
-- ==============================================================================
-- INSERT INTO storage.buckets (id, name, public) VALUES ('crop-images', 'crop-images', true) ON CONFLICT (id) DO NOTHING;
