import { notFound } from 'next/navigation';
import { transformNixOSRegistry, getServiceById, type Service } from '@/config/services';
import { ServicePage } from '@/components/services/ServicePage';

interface ServiceDetailPageProps {
  params: {
    id: string;
  };
}

async function getServices(): Promise<Service[]> {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';

  try {
    const response = await fetch(`${baseUrl}/api/services`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      return [];
    }

    const registry = await response.json();
    return transformNixOSRegistry(registry);
  } catch (error) {
    console.error('Error loading services:', error);
    return [];
  }
}

export async function generateStaticParams() {
  const services = await getServices();
  return services.map((service) => ({
    id: service.id,
  }));
}

export async function generateMetadata({ params }: ServiceDetailPageProps) {
  const { id } = await params;
  const services = await getServices();
  const service = getServiceById(services, id);

  if (!service) {
    return {
      title: 'Service Not Found',
    };
  }

  return {
    title: `${service.name} - Dashboard`,
    description: service.description,
  };
}

export default async function ServiceDetailPage({ params }: ServiceDetailPageProps) {
  const { id } = await params;
  const services = await getServices();
  const service = getServiceById(services, id);

  if (!service) {
    notFound();
  }

  return <ServicePage service={service} />;
}