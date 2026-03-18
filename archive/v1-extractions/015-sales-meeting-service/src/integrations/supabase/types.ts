export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      company_profiles: {
        Row: {
          company_id: string
          company_name: string | null
          contact_email: string | null
          contact_name: string | null
          created_at: string
          effective_date: string | null
          funding_type: string | null
          renewal_date: string | null
          total_employees: number | null
          total_enrolled: number | null
        }
        Insert: {
          company_id: string
          company_name?: string | null
          contact_email?: string | null
          contact_name?: string | null
          created_at?: string
          effective_date?: string | null
          funding_type?: string | null
          renewal_date?: string | null
          total_employees?: number | null
          total_enrolled?: number | null
        }
        Update: {
          company_id?: string
          company_name?: string | null
          contact_email?: string | null
          contact_name?: string | null
          created_at?: string
          effective_date?: string | null
          funding_type?: string | null
          renewal_date?: string | null
          total_employees?: number | null
          total_enrolled?: number | null
        }
        Relationships: []
      }
      meeting_1_verification: {
        Row: {
          business_issues: Json | null
          company_id: string
          compliance_info: Json | null
          created_at: string
          id: string
          renewal_verification: Json | null
          updated_at: string
        }
        Insert: {
          business_issues?: Json | null
          company_id: string
          compliance_info?: Json | null
          created_at?: string
          id?: string
          renewal_verification?: Json | null
          updated_at?: string
        }
        Update: {
          business_issues?: Json | null
          company_id?: string
          compliance_info?: Json | null
          created_at?: string
          id?: string
          renewal_verification?: Json | null
          updated_at?: string
        }
        Relationships: []
      }
      meeting_records: {
        Row: {
          company_id: string
          data: Json
          id: string
          meeting_number: number
          section: string
          updated_at: string
        }
        Insert: {
          company_id: string
          data?: Json
          id?: string
          meeting_number: number
          section: string
          updated_at?: string
        }
        Update: {
          company_id?: string
          data?: Json
          id?: string
          meeting_number?: number
          section?: string
          updated_at?: string
        }
        Relationships: []
      }
      meeting2_master: {
        Row: {
          company_id: string
          compliance_status: Json | null
          marketing_copy: string | null
          meeting_id: string
          montecarlo_results: Json | null
          presentation_mode: boolean | null
          updated_at: string
        }
        Insert: {
          company_id: string
          compliance_status?: Json | null
          marketing_copy?: string | null
          meeting_id?: string
          montecarlo_results?: Json | null
          presentation_mode?: boolean | null
          updated_at?: string
        }
        Update: {
          company_id?: string
          compliance_status?: Json | null
          marketing_copy?: string | null
          meeting_id?: string
          montecarlo_results?: Json | null
          presentation_mode?: boolean | null
          updated_at?: string
        }
        Relationships: []
      }
      montecarlo_constants: {
        Row: {
          active: boolean | null
          category: string | null
          constant_name: string
          constant_value: number | null
          description: string | null
          id: string
          last_updated: string
        }
        Insert: {
          active?: boolean | null
          category?: string | null
          constant_name: string
          constant_value?: number | null
          description?: string | null
          id?: string
          last_updated?: string
        }
        Update: {
          active?: boolean | null
          category?: string | null
          constant_name?: string
          constant_value?: number | null
          description?: string | null
          id?: string
          last_updated?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
