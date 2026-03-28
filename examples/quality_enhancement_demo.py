#!/usr/bin/env python3
"""
Quality Enhancement and Presets Demonstration

This script demonstrates the quality enhancement system and presets
available in the eventHorizon framework.
"""

import matplotlib.pyplot as plt
import eventHorizon
import time

def demonstrate_quality_levels():
    """Demonstrate different quality levels."""
    print("Quality Levels Demonstration")
    print("=" * 35)
    
    quality_levels = ["draft", "standard", "high", "publication"]
    
    for quality in quality_levels:
        print(f"\n🎯 Testing {quality.upper()} quality...")
        
        # Get quality configuration info
        config = eventHorizon.get_quality_config(quality)
        print(f"   Description: {config.description}")
        print(f"   Particles: {config.particle_count:,}")
        print(f"   Expected time: ~{config.expected_time_seconds:.1f}s")
        
        # Create visualization with progress monitoring
        fig, ax = eventHorizon.draw_blackhole_with_quality(
            quality_level=quality,
            inclination=80.0,
            show_progress=True
        )
        
        plt.tight_layout()
        plt.savefig(f'results/examples/quality_demo/{quality}_quality.png', 
                    facecolor='black', dpi=config.dpi)
        plt.show()

def demonstrate_use_case_presets():
    """Demonstrate different use case presets."""
    print("\nUse Case Presets Demonstration")
    print("=" * 35)
    
    use_cases = ["interactive", "batch_processing", "publication", "education", "research"]
    
    for use_case in use_cases:
        print(f"\n📋 Testing {use_case.upper()} preset...")
        
        # Get preset info
        preset = eventHorizon.get_use_case_preset(use_case)
        print(f"   Description: {preset['description']}")
        print(f"   Quality level: {preset['quality_level'].value}")
        
        # Create visualization
        fig, ax = eventHorizon.draw_blackhole_with_quality(
            use_case=use_case,
            inclination=80.0,
            show_progress=True
        )
        
        plt.tight_layout()
        plt.savefig(f'results/examples/quality_demo/{use_case}_preset.png', 
                    facecolor='black', dpi=150)
        plt.show()

def demonstrate_quality_comparison():
    """Demonstrate side-by-side quality comparison."""
    print("\nQuality Comparison Demonstration")
    print("=" * 40)
    
    # Create quality comparison
    results = eventHorizon.create_quality_comparison(
        inclination=85.0,
        quality_levels=["draft", "standard", "high"]
    )
    
    # Create combined figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('black')
    
    quality_levels = ["draft", "standard", "high"]
    
    for i, ((temp_fig, temp_ax), quality) in enumerate(zip(results, quality_levels)):
        # Copy visualization to combined plot
        axes[i].clear()
        axes[i].set_facecolor('black')
        
        for collection in temp_ax.collections:
            axes[i].add_collection(collection)
        
        axes[i].set_xlim(temp_ax.get_xlim())
        axes[i].set_ylim(temp_ax.get_ylim())
        axes[i].set_aspect('equal')
        axes[i].set_title(temp_ax.get_title(), color='white', fontsize=12)
        axes[i].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/quality_demo/quality_comparison.png', 
                facecolor='black', dpi=200)
    plt.show()

def demonstrate_progressive_enhancement():
    """Demonstrate progressive quality enhancement."""
    print("\nProgressive Enhancement Demonstration")
    print("=" * 45)
    
    # Create progressive enhancement demo
    results = eventHorizon.progressive_enhancement_demo(
        inclination=80.0,
        enhancement_steps=4
    )
    
    # Create combined figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.patch.set_facecolor('black')
    
    for i, (temp_fig, temp_ax) in enumerate(results):
        row, col = i // 2, i % 2
        
        # Copy visualization to combined plot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(temp_ax.get_title(), color='white', fontsize=12)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    plt.tight_layout()
    plt.savefig('results/examples/quality_demo/progressive_enhancement.png', 
                facecolor='black', dpi=200)
    plt.show()

def demonstrate_performance_benchmarking():
    """Demonstrate performance benchmarking."""
    print("\nPerformance Benchmarking Demonstration")
    print("=" * 45)
    
    # Run benchmark
    benchmark_results = eventHorizon.benchmark_quality_levels(
        inclination=80.0,
        runs_per_level=2  # Reduced for demo
    )
    
    # Create performance visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot execution times
    qualities = list(benchmark_results.keys())
    times = [benchmark_results[q]['avg_time'] for q in qualities]
    particle_counts = [benchmark_results[q]['particle_count'] for q in qualities]
    
    ax1.bar(qualities, times, color=['lightblue', 'orange', 'lightgreen'])
    ax1.set_ylabel('Average Execution Time (seconds)')
    ax1.set_title('Performance by Quality Level')
    ax1.grid(True, alpha=0.3)
    
    # Plot particle count vs time
    ax2.scatter(particle_counts, times, s=100, c=['lightblue', 'orange', 'lightgreen'])
    for i, quality in enumerate(qualities):
        ax2.annotate(quality, (particle_counts[i], times[i]), 
                    xytext=(5, 5), textcoords='offset points')
    ax2.set_xlabel('Particle Count')
    ax2.set_ylabel('Execution Time (seconds)')
    ax2.set_title('Particle Count vs Performance')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/examples/quality_demo/performance_benchmark.png', dpi=150)
    plt.show()
    
    return benchmark_results

def demonstrate_performance_recommendations():
    """Demonstrate performance recommendations."""
    print("\nPerformance Recommendations Demonstration")
    print("=" * 50)
    
    target_times = [2.0, 5.0, 10.0, 30.0]
    
    for target_time in target_times:
        print(f"\n🎯 Target time: {target_time}s")
        
        recommendations = eventHorizon.get_performance_recommendations(target_time)
        print(f"   Recommendation: {recommendations.get('suggestion', 'No data available')}")
        
        if 'particle_count' in recommendations:
            print(f"   Recommended particles: {recommendations['particle_count']:,}")
            print(f"   Expected time: {recommendations['expected_time']:.2f}s")

def demonstrate_custom_quality_presets():
    """Demonstrate creating custom quality presets."""
    print("\nCustom Quality Presets Demonstration")
    print("=" * 45)
    
    # Create custom preset by overriding standard quality
    print("\n🛠️  Creating custom preset...")
    
    custom_params = eventHorizon.apply_quality_preset(
        "standard",
        particle_count=15000,  # Override particle count
        power_scale=0.8,       # Override power scale
        inclination=75.0       # Add custom parameter
    )
    
    print(f"   Custom parameters: {custom_params}")
    
    # Use custom preset
    fig, ax = eventHorizon.draw_blackhole(**custom_params)
    ax.set_title("Custom Quality Preset", color='white')
    
    plt.tight_layout()
    plt.savefig('results/examples/quality_demo/custom_preset.png', 
                facecolor='black', dpi=150)
    plt.show()

def demonstrate_progress_monitoring():
    """Demonstrate progress monitoring capabilities."""
    print("\nProgress Monitoring Demonstration")
    print("=" * 40)
    
    print("\n📊 Creating visualization with detailed progress monitoring...")
    
    # Create high-quality visualization with progress monitoring
    fig, ax = eventHorizon.draw_blackhole_with_quality(
        quality_level="high",
        inclination=80.0,
        show_progress=True
    )
    
    plt.tight_layout()
    plt.savefig('results/examples/quality_demo/progress_monitored.png', 
                facecolor='black', dpi=200)
    plt.show()

def main():
    """Run all quality enhancement demonstrations."""
    print("EventHorizon Quality Enhancement and Presets Demo")
    print("=" * 55)
    
    # Create results directory
    import os
    os.makedirs('results/examples/quality_demo', exist_ok=True)
    
    # Run demonstrations
    demonstrate_quality_levels()
    demonstrate_use_case_presets()
    demonstrate_quality_comparison()
    demonstrate_progressive_enhancement()
    benchmark_results = demonstrate_performance_benchmarking()
    demonstrate_performance_recommendations()
    demonstrate_custom_quality_presets()
    demonstrate_progress_monitoring()
    
    print("\n" + "=" * 55)
    print("Quality Enhancement Demo Completed!")
    print("Results saved to: results/examples/quality_demo/")
    print("\nKey Features Demonstrated:")
    print("✅ Four quality levels: draft, standard, high, publication")
    print("✅ Five use case presets: interactive, batch, publication, education, research")
    print("✅ Progressive quality enhancement system")
    print("✅ Performance benchmarking and monitoring")
    print("✅ Automatic performance recommendations")
    print("✅ Custom quality preset creation")
    print("✅ Real-time progress monitoring")
    
    if benchmark_results:
        print(f"\nBenchmark Summary:")
        for quality, data in benchmark_results.items():
            print(f"  {quality.title():12} | {data['avg_time']:6.2f}s | {data['particle_count']:6,} particles")

if __name__ == "__main__":
    main()