import { notFound } from 'next/navigation';
import { transformNixOSRegistry, getServiceById, type Service } from '@/config/services';
import { ServicePage } from '@/components/services/ServicePage';
import fs from 'fs';

interface ServiceDetailPageProps {
  params: {
    id: string;
  };
}

async function getServices(): Promise<Service[]> {
  const servicesPath = process.env.SERVICES_CONFIG || '/etc/unified-dashboard/services.json';

  try {
    const rawData = fs.readFileSync(servicesPath, 'utf-8');
    const registry = JSON.parse(rawData);
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