import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, Sparkles, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

const Register: React.FC = () => {
  const { register: signup } = useAuth();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormValues) => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await signup(data);
    } catch (err: any) {
      setErrorMsg(
        err?.response?.data?.detail || 'Registration failed. The email may already be in use.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-tr from-slate-50 via-blue-50/20 to-purple-50/20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Brand header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <Sparkles className="h-8 w-8 text-blue-600 animate-pulse" />
            <span className="font-bold text-2xl tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              XE-Commerce
            </span>
          </Link>
          <h2 className="text-2xl font-extrabold text-slate-800">Create Account</h2>
          <p className="text-sm text-slate-500 mt-1">Start shopping smarter with integrated AI models</p>
        </div>

        {/* Card wrapper */}
        <div className="glass rounded-2xl shadow-xl p-8 border border-white/40 bg-white/80">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {errorMsg && (
              <div className="p-3.5 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs font-medium">
                {errorMsg}
              </div>
            )}

            {/* Username field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                User Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="john_doe"
                  {...register('username')}
                  className={`w-full px-4 py-3 pl-10 rounded-xl border bg-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition-all ${
                    errors.username ? 'border-red-300' : 'border-slate-200'
                  }`}
                />
                <User className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
              </div>
              {errors.username && (
                <p className="text-xs text-red-500 font-medium">{errors.username.message}</p>
              )}
            </div>

            {/* Email field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Email Address
              </label>
              <div className="relative">
                <input
                  type="email"
                  placeholder="name@example.com"
                  {...register('email')}
                  className={`w-full px-4 py-3 pl-10 rounded-xl border bg-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition-all ${
                    errors.email ? 'border-red-300' : 'border-slate-200'
                  }`}
                />
                <Mail className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
              </div>
              {errors.email && (
                <p className="text-xs text-red-500 font-medium">{errors.email.message}</p>
              )}
            </div>

            {/* Password field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  {...register('password')}
                  className={`w-full px-4 py-3 pl-10 pr-10 rounded-xl border bg-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition-all ${
                    errors.password ? 'border-red-300' : 'border-slate-200'
                  }`}
                />
                <Lock className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3.5 text-slate-400 hover:text-slate-600 focus:outline-none"
                >
                  {showPassword ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-500 font-medium">{errors.password.message}</p>
              )}
            </div>

            {/* Submit button */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 px-4 mt-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none shadow-md shadow-blue-500/10 flex items-center justify-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
            >
              {isSubmitting ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </motion.button>
          </form>

          {/* Login pointer */}
          <div className="text-center mt-6 text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700 transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;
